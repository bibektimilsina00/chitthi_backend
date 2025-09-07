"""WebSocket implementation for real-time messaging."""

import json
import uuid
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlmodel import Session

from app.core.db import engine
from app.models.user import User
from app.services import conversation_service, message_service

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for real-time messaging."""

    def __init__(self):
        # Store connections by user_id and device_id
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        # Store user info for each connection
        self.user_sessions: Dict[str, Dict[str, User]] = {}

    async def connect(
        self, websocket: WebSocket, user: User, device_id: str = "default"
    ):
        """Accept a WebSocket connection and store it."""
        await websocket.accept()

        user_id = str(user.id)
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}
            self.user_sessions[user_id] = {}

        self.active_connections[user_id][device_id] = websocket
        self.user_sessions[user_id][device_id] = user

        # Notify user about successful connection
        await self.send_personal_message(
            {
                "type": "connection_established",
                "message": "Connected to chat server",
                "user_id": user_id,
                "device_id": device_id,
            },
            user_id,
            device_id,
        )

    def disconnect(self, user_id: str, device_id: str = "default"):
        """Remove a WebSocket connection."""
        if user_id in self.active_connections:
            if device_id in self.active_connections[user_id]:
                del self.active_connections[user_id][device_id]
                del self.user_sessions[user_id][device_id]

            # Remove user entry if no devices connected
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                del self.user_sessions[user_id]

    async def send_personal_message(
        self, message: dict, user_id: str, device_id: str = "default"
    ):
        """Send a message to a specific user device."""
        if (
            user_id in self.active_connections
            and device_id in self.active_connections[user_id]
        ):
            websocket = self.active_connections[user_id][device_id]
            try:
                await websocket.send_text(json.dumps(message))
            except Exception:
                # Connection might be closed, remove it
                self.disconnect(user_id, device_id)

    async def send_to_all_user_devices(self, message: dict, user_id: str):
        """Send a message to all devices of a user."""
        if user_id in self.active_connections:
            for device_id in self.active_connections[user_id].copy():
                await self.send_personal_message(message, user_id, device_id)

    async def broadcast_to_conversation(
        self, message: dict, conversation_id: str, exclude_user: str | None = None
    ):
        """Broadcast a message to all members of a conversation."""
        # Get conversation members from database
        with Session(engine) as session:
            members = conversation_service.get_conversation_members(
                session=session,
                conversation_id=uuid.UUID(conversation_id),
                user_id=uuid.UUID(
                    exclude_user or "00000000-0000-0000-0000-000000000000"
                ),
            )

            for member in members:
                user_id = str(member.user_id)
                if user_id != exclude_user:
                    await self.send_to_all_user_devices(message, user_id)

    def get_online_users(self) -> List[str]:
        """Get list of currently online user IDs."""
        return list(self.active_connections.keys())

    def is_user_online(self, user_id: str) -> bool:
        """Check if a user is currently online."""
        return user_id in self.active_connections


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws/{device_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    device_id: str = "default",
):
    """
    WebSocket endpoint for real-time messaging.

    Handles:
    - Message sending/receiving
    - Typing indicators
    - Online status
    - Message delivery confirmations
    """
    user = None
    user_id = None

    try:
        # Authenticate user from WebSocket headers/query params
        # For now, we'll extract from query params - in production use JWT from headers
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=4001, reason="Authentication required")
            return

        # Get user from token (simplified - use your auth logic)
        with Session(engine) as session:
            # For now, just get the first user - in production implement proper auth
            from sqlmodel import select

            stmt = select(User).limit(1)
            user = session.exec(stmt).first()
            if not user:
                await websocket.close(code=4001, reason="No users found")
                return

        user_id = str(user.id)
        await manager.connect(websocket, user, device_id)

        while True:
            # Receive message from WebSocket
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Handle different message types
            message_type = message_data.get("type")

            if message_type == "send_message":
                await handle_send_message(message_data, user, device_id)
            elif message_type == "typing_start":
                await handle_typing_indicator(message_data, user_id, True)
            elif message_type == "typing_stop":
                await handle_typing_indicator(message_data, user_id, False)
            elif message_type == "mark_read":
                await handle_mark_read(message_data, user_id)
            elif message_type == "ping":
                await manager.send_personal_message(
                    {"type": "pong"}, user_id, device_id
                )
            else:
                await manager.send_personal_message(
                    {
                        "type": "error",
                        "message": f"Unknown message type: {message_type}",
                    },
                    user_id,
                    device_id,
                )

    except WebSocketDisconnect:
        if user_id:
            manager.disconnect(user_id, device_id)
    except Exception as e:
        if user_id:
            manager.disconnect(user_id, device_id)
        print(f"WebSocket error: {e}")


async def handle_send_message(message_data: dict, user: User, device_id: str):
    """Handle sending a new message."""
    try:
        conversation_id = message_data.get("conversation_id")
        content = message_data.get("content")
        message_type = message_data.get("message_type", "text")

        if not conversation_id or not content:
            await manager.send_personal_message(
                {"type": "error", "message": "Missing conversation_id or content"},
                str(user.id),
                device_id,
            )
            return

        # Create message in database
        with Session(engine) as session:
            from app.schemas.message import MessageCreate

            message_create = MessageCreate(
                conversation_id=uuid.UUID(conversation_id),
                ciphertext=content,  # In production, this should be encrypted
                ciphertext_nonce="dummy_nonce",
                message_type=message_type,
            )

            message = message_service.create_encrypted_message(
                session=session,
                message_create=message_create,
                sender_id=user.id,
                recipient_encrypted_keys=[],  # Simplified for now
            )

            # Broadcast to conversation members
            broadcast_message = {
                "type": "new_message",
                "message": {
                    "id": str(message.id),
                    "conversation_id": str(message.conversation_id),
                    "sender_id": str(message.sender_id),
                    "content": content,
                    "message_type": message_type,
                    "created_at": message.created_at.isoformat(),
                    "sender": {
                        "id": str(user.id),
                        "email": user.email,
                        "display_name": user.display_name,
                    },
                },
            }

            await manager.broadcast_to_conversation(
                broadcast_message, conversation_id, exclude_user=str(user.id)
            )

            # Send confirmation to sender
            await manager.send_personal_message(
                {"type": "message_sent", "message": broadcast_message["message"]},
                str(user.id),
                device_id,
            )

    except Exception as e:
        await manager.send_personal_message(
            {"type": "error", "message": f"Failed to send message: {str(e)}"},
            str(user.id),
            device_id,
        )


async def handle_typing_indicator(message_data: dict, user_id: str, is_typing: bool):
    """Handle typing indicators."""
    conversation_id = message_data.get("conversation_id")
    if not conversation_id:
        return

    typing_message = {
        "type": "typing_indicator",
        "conversation_id": conversation_id,
        "user_id": user_id,
        "is_typing": is_typing,
    }

    await manager.broadcast_to_conversation(
        typing_message, conversation_id, exclude_user=user_id
    )


async def handle_mark_read(message_data: dict, user_id: str):
    """Handle marking messages as read."""
    message_id = message_data.get("message_id")
    conversation_id = message_data.get("conversation_id")

    if not message_id:
        return

    # Update read status in database
    with Session(engine) as session:
        # Simplified - in production use proper read status tracking
        pass

    # Notify sender about read receipt
    read_receipt = {
        "type": "message_read",
        "message_id": message_id,
        "conversation_id": conversation_id,
        "read_by": user_id,
    }

    if conversation_id:
        await manager.broadcast_to_conversation(
            read_receipt, conversation_id, exclude_user=user_id
        )


# REST endpoints for WebSocket info
@router.get("/online-users")
async def get_online_users():
    """Get list of currently online users."""
    return {"online_users": manager.get_online_users()}


@router.get("/user/{user_id}/status")
async def get_user_status(user_id: str):
    """Check if a specific user is online."""
    return {"user_id": user_id, "is_online": manager.is_user_online(user_id)}

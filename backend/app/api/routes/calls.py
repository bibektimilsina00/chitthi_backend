"""Audio and Video Call API endpoints."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlmodel import Session

from app.api.deps import CurrentUser, SessionDep
from app.schemas.common import Message

router = APIRouter()


class CallInitiateRequest(BaseModel):
    participants: List[str]
    call_type: str = "audio"


class CallManager:
    """Manages active audio/video calls."""

    def __init__(self):
        self.active_calls: Dict[str, Dict] = {}  # call_id -> call_info
        self.user_calls: Dict[str, str] = {}  # user_id -> call_id
        self.call_connections: Dict[str, List[WebSocket]] = {}  # call_id -> websockets

    def create_call(
        self,
        call_id: str,
        caller_id: str,
        participants: List[str],
        call_type: str = "audio",
    ):
        """Create a new call session."""
        self.active_calls[call_id] = {
            "id": call_id,
            "caller_id": caller_id,
            "participants": participants,
            "type": call_type,  # "audio" or "video"
            "status": "initiating",
            "started_at": datetime.utcnow(),
            "ended_at": None,
        }

        # Map users to this call
        for user_id in participants:
            self.user_calls[user_id] = call_id

        self.call_connections[call_id] = []
        return self.active_calls[call_id]

    def add_connection(self, call_id: str, websocket: WebSocket):
        """Add a WebSocket connection to a call."""
        if call_id in self.call_connections:
            self.call_connections[call_id].append(websocket)

    def remove_connection(self, call_id: str, websocket: WebSocket):
        """Remove a WebSocket connection from a call."""
        if call_id in self.call_connections:
            if websocket in self.call_connections[call_id]:
                self.call_connections[call_id].remove(websocket)

    def end_call(self, call_id: str):
        """End a call and cleanup."""
        if call_id in self.active_calls:
            self.active_calls[call_id]["status"] = "ended"
            self.active_calls[call_id]["ended_at"] = datetime.utcnow()

            # Remove user mappings
            participants = self.active_calls[call_id]["participants"]
            for user_id in participants:
                if user_id in self.user_calls:
                    del self.user_calls[user_id]

            # Close all connections
            if call_id in self.call_connections:
                del self.call_connections[call_id]

    def get_call(self, call_id: str) -> Optional[Dict]:
        """Get call information."""
        return self.active_calls.get(call_id)

    def get_user_active_call(self, user_id: str) -> Optional[str]:
        """Get active call ID for a user."""
        return self.user_calls.get(user_id)


# Global call manager
call_manager = CallManager()


@router.post("/initiate")
async def initiate_call(
    request: CallInitiateRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Initiate an audio or video call.

    Args:
        request: CallInitiateRequest containing participants and call_type
    """
    # Import the WebSocket manager
    from app.api.routes.websocket import manager
    
    # Check if current user is already in a call
    existing_call = call_manager.get_user_active_call(str(current_user.id))
    if existing_call:
        raise HTTPException(status_code=400, detail="User already in an active call")

    # Validate participants exist and are contacts
    # In production, add proper validation

    call_id = str(uuid.uuid4())
    all_participants = [str(current_user.id)] + request.participants

    call_info = call_manager.create_call(
        call_id=call_id,
        caller_id=str(current_user.id),
        participants=all_participants,
        call_type=request.call_type,
    )

    # Send incoming call notifications to other participants via WebSocket
    call_notification = {
        "type": "incoming_call",
        "call_id": call_id,
        "caller_id": str(current_user.id),
        "caller_name": current_user.display_name or current_user.username,
        "call_type": request.call_type,
        "signaling_url": f"/api/v1/calls/{call_id}/signaling",
    }
    
    # Notify all participants except the caller
    for participant_id in request.participants:
        await manager.send_to_all_user_devices(call_notification, participant_id)

    return {
        "call_id": call_id,
        "status": "initiated",
        "participants": all_participants,
        "type": request.call_type,
        "signaling_url": f"/api/v1/calls/{call_id}/signaling",
    }


@router.post("/{call_id}/join")
def join_call(call_id: str, session: SessionDep, current_user: CurrentUser) -> Any:
    """Join an existing call."""
    call_info = call_manager.get_call(call_id)
    if not call_info:
        raise HTTPException(status_code=404, detail="Call not found")

    user_id = str(current_user.id)
    if user_id not in call_info["participants"]:
        raise HTTPException(status_code=403, detail="Not invited to this call")

    # Check if user is already in another call
    existing_call = call_manager.get_user_active_call(user_id)
    if existing_call and existing_call != call_id:
        raise HTTPException(status_code=400, detail="User already in another call")

    return {
        "call_id": call_id,
        "status": "joined",
        "signaling_url": f"/api/v1/calls/{call_id}/signaling",
    }


@router.post("/{call_id}/end")
def end_call(call_id: str, session: SessionDep, current_user: CurrentUser) -> Message:
    """End a call."""
    call_info = call_manager.get_call(call_id)
    if not call_info:
        raise HTTPException(status_code=404, detail="Call not found")

    user_id = str(current_user.id)

    # Only caller or participant can end call
    if user_id not in call_info["participants"]:
        raise HTTPException(status_code=403, detail="Not authorized to end this call")

    call_manager.end_call(call_id)

    # Log call in database for history
    # In production, save call logs

    return Message(message="Call ended")


@router.get("/{call_id}")
def get_call_info(call_id: str, session: SessionDep, current_user: CurrentUser) -> Any:
    """Get call information."""
    call_info = call_manager.get_call(call_id)
    if not call_info:
        raise HTTPException(status_code=404, detail="Call not found")

    user_id = str(current_user.id)
    if user_id not in call_info["participants"]:
        raise HTTPException(status_code=403, detail="Not authorized to view this call")

    return call_info


@router.websocket("/{call_id}/signaling")
async def call_signaling_websocket(websocket: WebSocket, call_id: str):
    """
    WebSocket endpoint for WebRTC signaling.

    Handles:
    - SDP offers/answers
    - ICE candidates
    - Call control messages
    """
    try:
        await websocket.accept()

        # Validate call exists
        call_info = call_manager.get_call(call_id)
        if not call_info:
            await websocket.close(code=4004, reason="Call not found")
            return

        call_manager.add_connection(call_id, websocket)
    except Exception as e:
        print(f"WebSocket connection failed: {e}")
        try:
            await websocket.close(code=4000, reason="Connection failed")
        except:
            pass
        return

    try:
        while True:
            # Receive signaling message
            data = await websocket.receive_text()
            import json
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                print(f"Invalid JSON received: {data}")
                continue

            message_type = message.get("type")

            if message_type == "offer":
                # Forward SDP offer to other participants
                await broadcast_to_call(call_id, message, exclude_ws=websocket)

            elif message_type == "answer":
                # Forward SDP answer to caller
                await broadcast_to_call(call_id, message, exclude_ws=websocket)

            elif message_type == "ice-candidate":
                # Forward ICE candidate to other participants
                await broadcast_to_call(call_id, message, exclude_ws=websocket)

            elif message_type == "mute":
                # Broadcast mute status
                await broadcast_to_call(
                    call_id,
                    {
                        "type": "participant_muted",
                        "user_id": message.get("user_id"),
                        "muted": message.get("muted", True),
                    },
                    exclude_ws=websocket,
                )

            elif message_type == "video_toggle":
                # Broadcast video status
                await broadcast_to_call(
                    call_id,
                    {
                        "type": "participant_video",
                        "user_id": message.get("user_id"),
                        "video_enabled": message.get("video_enabled", False),
                    },
                    exclude_ws=websocket,
                )

    except WebSocketDisconnect:
        call_manager.remove_connection(call_id, websocket)
    except Exception as e:
        print(f"WebRTC signaling error: {e}")
        call_manager.remove_connection(call_id, websocket)


async def broadcast_to_call(
    call_id: str, message: dict, exclude_ws: WebSocket | None = None
):
    """Broadcast a message to all participants in a call."""
    if call_id in call_manager.call_connections:
        import json

        message_str = json.dumps(message)

        for websocket in call_manager.call_connections[call_id].copy():
            if websocket != exclude_ws:
                try:
                    await websocket.send_text(message_str)
                except Exception:
                    # Connection might be closed
                    call_manager.remove_connection(call_id, websocket)


@router.get("/")
def get_active_calls(session: SessionDep, current_user: CurrentUser) -> Any:
    """Get active calls for current user."""
    user_id = str(current_user.id)
    active_call_id = call_manager.get_user_active_call(user_id)

    if not active_call_id:
        return {"active_calls": []}

    call_info = call_manager.get_call(active_call_id)
    return {"active_calls": [call_info] if call_info else []}

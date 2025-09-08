import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Query, WebSocket

from app.api.deps import CurrentUser, SessionDep
from app.schemas import Message
from app.services import message_service

router = APIRouter()


@router.websocket("/ws")
async def websocket_redirect(websocket: WebSocket):
    """
    Redirect to the correct WebSocket endpoint.
    The real WebSocket endpoint is at /api/v1/chat/ws/{device_id}
    """
    await websocket.close(
        code=4002,
        reason="WebSocket moved to /api/v1/chat/ws/{device_id}?token=JWT_TOKEN",
    )


@router.get("/")
def read_messages(
    session: SessionDep,
    current_user: CurrentUser,
    conversation_id: uuid.UUID = Query(..., description="Conversation ID"),
    skip: int = 0,
    limit: int = Query(default=100, le=100),
) -> Any:
    """
    Retrieve messages from a conversation.
    """
    try:
        messages = message_service.get_conversation_messages(
            session=session,
            conversation_id=conversation_id,
            user_id=current_user.id,
            skip=skip,
            limit=limit,
        )
        return {"data": messages, "count": len(messages)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/")
def create_message(
    session: SessionDep,
    current_user: CurrentUser,
    *,
    message_data: dict,
    conversation_id: uuid.UUID = Query(None),
    message_type: str = Query("text"),
) -> Any:
    """
    Create new encrypted message.

    Supports two formats:
    1. All data in JSON body:
    {
        "conversation_id": "uuid",
        "ciphertext": "encrypted_content",
        "message_type": "text|image|file|etc",
        "recipient_keys": [{"user_id": "uuid", "encrypted_key": "key"}]
    }

    2. conversation_id and message_type as query params with ciphertext in body:
    ?conversation_id=uuid&message_type=text
    {
        "ciphertext": "encrypted_content",
        "recipient_keys": [{"user_id": "uuid", "encrypted_key": "key"}]
    }
    """
    try:
        from app.schemas.message import MessageCreate

        # Merge query params with JSON body data (JSON body takes precedence)
        final_conversation_id = message_data.get("conversation_id") or conversation_id
        final_message_type = message_data.get("message_type", message_type)
        ciphertext = message_data.get("ciphertext")
        recipient_keys = message_data.get("recipient_keys", [])

        if not final_conversation_id or not ciphertext:
            raise HTTPException(
                status_code=422, detail="conversation_id and ciphertext are required"
            )

        message_create = MessageCreate(
            conversation_id=(
                final_conversation_id
                if isinstance(final_conversation_id, uuid.UUID)
                else uuid.UUID(final_conversation_id)
            ),
            ciphertext=ciphertext,
            ciphertext_nonce="generated_nonce",  # Should be generated properly
            message_type=final_message_type,
        )
        message = message_service.create_encrypted_message(
            session=session,
            message_create=message_create,
            sender_id=current_user.id,
            recipient_encrypted_keys=recipient_keys,
        )
        session.commit()  # Commit the transaction
        session.refresh(message)  # Refresh to get updated data
        return message
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Invalid UUID format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{message_id}")
def read_message(
    session: SessionDep, current_user: CurrentUser, message_id: uuid.UUID
) -> Any:
    """
    Get message by ID.
    """
    try:
        # Get the message from CRUD
        from app import crud

        message = crud.message.get(session=session, id=message_id)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        return message
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{message_id}")
def delete_message(
    session: SessionDep, current_user: CurrentUser, message_id: uuid.UUID
) -> Message:
    """
    Delete a message.
    """
    try:
        success = message_service.soft_delete_message(
            session=session, message_id=message_id, user_id=current_user.id
        )
        if not success:
            raise HTTPException(
                status_code=404, detail="Message not found or no permission"
            )
        return Message(message="Message deleted")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{message_id}/read")
def mark_as_read(
    session: SessionDep,
    current_user: CurrentUser,
    message_id: uuid.UUID,
    device_id: uuid.UUID = Query(description="Device ID"),
) -> Message:
    """
    Mark message as read.
    """
    try:
        success = message_service.mark_message_as_read(
            session=session,
            message_id=message_id,
            user_id=current_user.id,
            device_id=device_id,
        )
        if not success:
            raise HTTPException(status_code=404, detail="Message not found")
        return Message(message="Message marked as read")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

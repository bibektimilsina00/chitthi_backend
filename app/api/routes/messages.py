import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.api.deps import CurrentUser, SessionDep
from app.schemas import Message
from app.services import message_service

router = APIRouter()


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
    conversation_id: uuid.UUID,
    ciphertext: str,
    message_type: str = "text",
    recipient_keys: list[dict] = [],
) -> Any:
    """
    Create new encrypted message.
    """
    try:
        from app.schemas.message import MessageCreate

        message_create = MessageCreate(
            conversation_id=conversation_id,
            ciphertext=ciphertext,
            ciphertext_nonce="generated_nonce",  # Should be generated properly
            message_type=message_type,
        )
        message = message_service.create_encrypted_message(
            session=session,
            message_create=message_create,
            sender_id=current_user.id,
            recipient_encrypted_keys=recipient_keys,
        )
        return message
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

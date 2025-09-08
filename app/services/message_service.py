"""Message service for handling encrypted messaging operations."""

import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session

from app import crud
from app.models.message import Message, MessageAttachment, MessageEncryptedKeys
from app.schemas.message import MessageCreate, MessageUpdate


class MessageService:
    """Service for handling message operations with E2E encryption."""

    def create_encrypted_message(
        self,
        session: Session,
        *,
        message_create: MessageCreate,
        sender_id: uuid.UUID,
        recipient_encrypted_keys: list[dict[str, Any]],
    ) -> Message:
        """
        Create an encrypted message with per-recipient keys.

        Args:
            session: Database session
            message_create: Message creation data
            sender_id: ID of the message sender
            recipient_encrypted_keys: List of encrypted keys for each recipient device
                Format: [{"user_id": "...", "device_id": "...", "encrypted_key": "...", "nonce": "..."}]
        """
        from datetime import datetime

        from app.models.message import Message

        # Create the message directly with the Message model to include sender_id
        message_data = message_create.model_dump()
        message_data["sender_id"] = sender_id
        message_data["id"] = uuid.uuid4()
        message_data["created_at"] = datetime.utcnow()

        message = Message(**message_data)
        session.add(message)
        session.flush()  # Flush to get the ID without committing
        session.refresh(message)

        # Create encrypted keys for each recipient device
        for key_data in recipient_encrypted_keys:
            encrypted_key = MessageEncryptedKeys(
                message_id=message.id,
                recipient_user_id=key_data["user_id"],
                recipient_device_id=key_data["device_id"],
                encrypted_key=key_data["encrypted_key"],
                nonce=key_data["nonce"],
                key_algo=key_data.get("key_algo", "x25519-aead"),
            )
            session.add(encrypted_key)

        # Let the route handler manage the commit
        session.flush()  # Ensure all objects are persisted and have IDs
        return message

    def get_conversation_messages(
        self,
        session: Session,
        *,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Message]:
        """Get messages for a conversation that the user can decrypt."""
        # First verify user is member of conversation
        member = crud.conversation_member.get_by_conversation_and_user(
            session, conversation_id=conversation_id, user_id=user_id
        )
        if not member:
            return []

        # Get messages
        messages = crud.message.get_conversation_messages(
            session, conversation_id=conversation_id, skip=skip, limit=limit
        )

        return messages

    def get_message_keys_for_user(
        self, session: Session, *, message_id: uuid.UUID, user_id: uuid.UUID
    ) -> list[MessageEncryptedKeys]:
        """Get all encrypted keys for a message that belong to a user."""
        return crud.message_encrypted_keys.get_keys_for_message_and_user(
            session, message_id=message_id, user_id=user_id
        )

    def mark_message_as_read(
        self,
        session: Session,
        *,
        message_id: uuid.UUID,
        user_id: uuid.UUID,
        device_id: uuid.UUID,
    ) -> bool:
        """Mark a message as read by updating its status."""
        crud.message_status.update_status(
            session,
            message_id=message_id,
            user_id=user_id,
            status="read",
            device_id=device_id,
        )
        return True

    def mark_message_as_delivered(
        self,
        session: Session,
        *,
        message_id: uuid.UUID,
        user_id: uuid.UUID,
        device_id: uuid.UUID,
    ) -> bool:
        """Mark a message as delivered."""
        crud.message_status.update_status(
            session,
            message_id=message_id,
            user_id=user_id,
            status="delivered",
            device_id=device_id,
        )
        return True

    def edit_message(
        self,
        session: Session,
        *,
        message_id: uuid.UUID,
        user_id: uuid.UUID,
        new_ciphertext: str,
        new_preview_hash: str | None = None,
    ) -> Message | None:
        """Edit a message (only by sender)."""
        message = crud.message.get(session, id=message_id)
        if not message or message.sender_id != user_id:
            return None

        # Store edit history
        edit_history = message.edit_history or []
        edit_history.append(
            {
                "edited_at": datetime.utcnow().isoformat(),
                "previous_ciphertext": message.ciphertext,
                "previous_preview_hash": message.preview_text_hash,
            }
        )

        # Update message
        update_data = {
            "ciphertext": new_ciphertext,
            "is_edited": True,
            "edit_history": edit_history,
            "updated_at": datetime.utcnow(),
        }

        if new_preview_hash:
            update_data["preview_text_hash"] = new_preview_hash

        return crud.message.update(session=session, db_obj=message, obj_in=update_data)

    def soft_delete_message(
        self, session: Session, *, message_id: uuid.UUID, user_id: uuid.UUID
    ) -> Message | None:
        """Soft delete a message (only by sender)."""
        return crud.message.mark_as_deleted(
            session, message_id=message_id, user_id=user_id
        )

    def react_to_message(
        self,
        session: Session,
        *,
        message_id: uuid.UUID,
        user_id: uuid.UUID,
        reaction: str,
    ) -> bool:
        """Add or remove a reaction to a message."""
        # Verify user can access the message
        message = crud.message.get(session, id=message_id)
        if not message:
            return False

        # Verify user is member of conversation
        member = crud.conversation_member.get_by_conversation_and_user(
            session, conversation_id=message.conversation_id, user_id=user_id
        )
        if not member:
            return False

        # Toggle reaction
        crud.message_reaction.toggle_reaction(
            session, message_id=message_id, user_id=user_id, reaction=reaction
        )
        return True

    def star_message(
        self, session: Session, *, message_id: uuid.UUID, user_id: uuid.UUID
    ) -> bool:
        """Star or unstar a message for a user."""
        # Verify user can access the message
        message = crud.message.get(session, id=message_id)
        if not message:
            return False

        # Verify user is member of conversation
        member = crud.conversation_member.get_by_conversation_and_user(
            session, conversation_id=message.conversation_id, user_id=user_id
        )
        if not member:
            return False

        # Toggle star
        crud.starred_messages.toggle_star(
            session, message_id=message_id, user_id=user_id
        )
        return True

    def get_starred_messages(
        self, session: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[dict]:
        """Get starred messages for a user with message details."""
        starred = crud.starred_messages.get_user_starred_messages(
            session, user_id=user_id, skip=skip, limit=limit
        )

        result = []
        for star in starred:
            message = crud.message.get(session, id=star.message_id)
            if message:
                result.append({"starred_at": star.starred_at, "message": message})

        return result

    def save_draft(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        conversation_id: uuid.UUID,
        draft_text_enc: str,
        attachments: dict | None = None,
    ) -> bool:
        """Save a message draft for a user in a conversation."""
        # Verify user is member of conversation
        member = crud.conversation_member.get_by_conversation_and_user(
            session, conversation_id=conversation_id, user_id=user_id
        )
        if not member:
            return False

        crud.message_drafts.save_draft(
            session,
            user_id=user_id,
            conversation_id=conversation_id,
            draft_text_enc=draft_text_enc,
            attachments=attachments,
        )
        return True

    def get_draft(
        self, session: Session, *, user_id: uuid.UUID, conversation_id: uuid.UUID
    ) -> dict | None:
        """Get draft for a user in a conversation."""
        draft = crud.message_drafts.get_conversation_draft(
            session, user_id=user_id, conversation_id=conversation_id
        )
        if draft:
            return {
                "draft_text_enc": draft.draft_text_enc,
                "attachments": draft.attachments,
                "updated_at": draft.updated_at,
            }
        return None


message_service = MessageService()

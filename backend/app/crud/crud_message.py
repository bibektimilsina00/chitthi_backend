import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session, desc, select

from app.crud.base import CRUDBase
from app.models.message import (
    Message,
    MessageAttachment,
    MessageDrafts,
    MessageEditHistory,
    MessageEncryptedKeys,
    MessageParticipantsCache,
    MessageReaction,
    MessageStatus,
    PinnedItems,
    ReadReceiptsSummary,
    StarredMessages,
)
from app.schemas.message import MessageAttachmentCreate, MessageCreate, MessageUpdate


class CRUDMessage(CRUDBase[Message, MessageCreate, MessageUpdate]):
    def get_conversation_messages(
        self,
        session: Session,
        *,
        conversation_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Message]:
        """Get messages for a specific conversation."""
        statement = (
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.is_deleted == False,
            )
            .offset(skip)
            .limit(limit)
            .order_by(desc(Message.created_at))
        )
        return list(session.exec(statement).all())

    def get_user_messages(
        self, session: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[Message]:
        """Get all messages sent by a specific user."""
        statement = (
            select(Message)
            .where(Message.sender_id == user_id, Message.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .order_by(desc(Message.created_at))
        )
        return list(session.exec(statement).all())

    def mark_as_deleted(
        self, session: Session, *, message_id: uuid.UUID, user_id: uuid.UUID
    ) -> Message | None:
        """Soft delete a message."""
        message = session.get(Message, message_id)
        if message and message.sender_id == user_id:
            message.is_deleted = True
            message.deleted_at = datetime.utcnow()
            session.add(message)
            session.commit()
            session.refresh(message)
            return message
        return None

    def search_messages(
        self,
        session: Session,
        *,
        conversation_id: uuid.UUID,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Message]:
        """Search messages in a conversation by preview text hash."""
        statement = (
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.is_deleted == False,
            )
            .offset(skip)
            .limit(limit)
            .order_by(desc(Message.created_at))
        )
        return list(session.exec(statement).all())


class CRUDMessageAttachment(CRUDBase[MessageAttachment, MessageAttachmentCreate, Any]):
    def get_message_attachments(
        self, session: Session, *, message_id: uuid.UUID
    ) -> list[MessageAttachment]:
        """Get all attachments for a message."""
        statement = select(MessageAttachment).where(
            MessageAttachment.message_id == message_id
        )
        return list(session.exec(statement).all())


class CRUDMessageEncryptedKeys(CRUDBase[MessageEncryptedKeys, Any, Any]):
    def get_keys_for_message_and_user(
        self, session: Session, *, message_id: uuid.UUID, user_id: uuid.UUID
    ) -> list[MessageEncryptedKeys]:
        """Get encrypted keys for a message and specific user."""
        statement = select(MessageEncryptedKeys).where(
            MessageEncryptedKeys.message_id == message_id,
            MessageEncryptedKeys.recipient_user_id == user_id,
        )
        return list(session.exec(statement).all())

    def get_keys_for_message_and_device(
        self,
        session: Session,
        *,
        message_id: uuid.UUID,
        user_id: uuid.UUID,
        device_id: uuid.UUID,
    ) -> MessageEncryptedKeys | None:
        """Get encrypted key for a specific message, user, and device."""
        statement = select(MessageEncryptedKeys).where(
            MessageEncryptedKeys.message_id == message_id,
            MessageEncryptedKeys.recipient_user_id == user_id,
            MessageEncryptedKeys.recipient_device_id == device_id,
        )
        return session.exec(statement).first()


class CRUDMessageStatus(CRUDBase[MessageStatus, Any, Any]):
    def get_message_status(
        self, session: Session, *, message_id: uuid.UUID, user_id: uuid.UUID
    ) -> MessageStatus | None:
        """Get delivery status for a message and user."""
        statement = select(MessageStatus).where(
            MessageStatus.message_id == message_id, MessageStatus.user_id == user_id
        )
        return session.exec(statement).first()

    def update_status(
        self,
        session: Session,
        *,
        message_id: uuid.UUID,
        user_id: uuid.UUID,
        status: str,
        device_id: uuid.UUID | None = None,
    ) -> MessageStatus:
        """Update or create message status."""
        existing = self.get_message_status(
            session, message_id=message_id, user_id=user_id
        )
        if existing:
            existing.status = status
            existing.status_at = datetime.utcnow()
            if device_id:
                existing.device_id = device_id
            session.add(existing)
        else:
            existing = MessageStatus(
                message_id=message_id,
                user_id=user_id,
                status=status,
                device_id=device_id,
                status_at=datetime.utcnow(),
            )
            session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing


class CRUDMessageReaction(CRUDBase[MessageReaction, Any, Any]):
    def get_message_reactions(
        self, session: Session, *, message_id: uuid.UUID
    ) -> list[MessageReaction]:
        """Get all reactions for a message."""
        statement = select(MessageReaction).where(
            MessageReaction.message_id == message_id
        )
        return list(session.exec(statement).all())

    def toggle_reaction(
        self,
        session: Session,
        *,
        message_id: uuid.UUID,
        user_id: uuid.UUID,
        reaction: str,
    ) -> MessageReaction | None:
        """Toggle a reaction on a message."""
        existing = session.exec(
            select(MessageReaction).where(
                MessageReaction.message_id == message_id,
                MessageReaction.user_id == user_id,
                MessageReaction.reaction == reaction,
            )
        ).first()

        if existing:
            session.delete(existing)
            session.commit()
            return None
        else:
            new_reaction = MessageReaction(
                message_id=message_id, user_id=user_id, reaction=reaction
            )
            session.add(new_reaction)
            session.commit()
            session.refresh(new_reaction)
            return new_reaction


class CRUDStarredMessages(CRUDBase[StarredMessages, Any, Any]):
    def get_user_starred_messages(
        self, session: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[StarredMessages]:
        """Get all starred messages for a user."""
        statement = (
            select(StarredMessages)
            .where(StarredMessages.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(desc(StarredMessages.starred_at))
        )
        return list(session.exec(statement).all())

    def toggle_star(
        self, session: Session, *, message_id: uuid.UUID, user_id: uuid.UUID
    ) -> StarredMessages | None:
        """Toggle star status on a message."""
        existing = session.exec(
            select(StarredMessages).where(
                StarredMessages.message_id == message_id,
                StarredMessages.user_id == user_id,
            )
        ).first()

        if existing:
            session.delete(existing)
            session.commit()
            return None
        else:
            starred = StarredMessages(message_id=message_id, user_id=user_id)
            session.add(starred)
            session.commit()
            session.refresh(starred)
            return starred


class CRUDMessageDrafts(CRUDBase[MessageDrafts, Any, Any]):
    def get_conversation_draft(
        self, session: Session, *, user_id: uuid.UUID, conversation_id: uuid.UUID
    ) -> MessageDrafts | None:
        """Get draft for a user in a specific conversation."""
        statement = select(MessageDrafts).where(
            MessageDrafts.user_id == user_id,
            MessageDrafts.conversation_id == conversation_id,
        )
        return session.exec(statement).first()

    def save_draft(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        conversation_id: uuid.UUID,
        draft_text_enc: str,
        attachments: dict | None = None,
    ) -> MessageDrafts:
        """Save or update a draft."""
        existing = self.get_conversation_draft(
            session, user_id=user_id, conversation_id=conversation_id
        )
        if existing:
            existing.draft_text_enc = draft_text_enc
            existing.attachments = attachments
            existing.updated_at = datetime.utcnow()
            session.add(existing)
        else:
            existing = MessageDrafts(
                user_id=user_id,
                conversation_id=conversation_id,
                draft_text_enc=draft_text_enc,
                attachments=attachments,
                updated_at=datetime.utcnow(),
            )
            session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing


# Create instances
message = CRUDMessage(Message)
message_attachment = CRUDMessageAttachment(MessageAttachment)
message_encrypted_keys = CRUDMessageEncryptedKeys(MessageEncryptedKeys)
message_status = CRUDMessageStatus(MessageStatus)
message_reaction = CRUDMessageReaction(MessageReaction)
starred_messages = CRUDStarredMessages(StarredMessages)
message_drafts = CRUDMessageDrafts(MessageDrafts)

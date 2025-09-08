import uuid
from typing import Any

from sqlmodel import Session, desc, select

from app.crud.base import CRUDBase
from app.models.conversation import Conversation, ConversationMember
from app.schemas.conversation import ConversationCreate, ConversationUpdate


class CRUDConversation(CRUDBase[Conversation, ConversationCreate, ConversationUpdate]):
    def get_user_conversations(
        self, session: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[Conversation]:
        """Get all conversations for a specific user."""
        statement = (
            select(Conversation)
            .join(ConversationMember)
            .where(ConversationMember.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(desc(Conversation.updated_at))
        )
        return list(session.exec(statement).all())


class CRUDConversationMember(CRUDBase[ConversationMember, Any, Any]):
    def get_by_conversation_and_user(
        self, session: Session, *, conversation_id: uuid.UUID, user_id: uuid.UUID
    ) -> ConversationMember | None:
        statement = select(ConversationMember).where(
            ConversationMember.conversation_id == conversation_id,
            ConversationMember.user_id == user_id,
        )
        return session.exec(statement).first()

    def get_conversation_members(
        self, session: Session, *, conversation_id: uuid.UUID
    ) -> list[ConversationMember]:
        statement = select(ConversationMember).where(
            ConversationMember.conversation_id == conversation_id
        )
        return list(session.exec(statement).all())


# Create instances
conversation = CRUDConversation(Conversation)
conversation_member = CRUDConversationMember(ConversationMember)

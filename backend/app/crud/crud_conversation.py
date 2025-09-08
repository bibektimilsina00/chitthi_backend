import uuid
from typing import Any

from sqlmodel import Session, desc, select

from app.crud.base import CRUDBase
from app.models.conversation import Conversation, ConversationMember
from app.models.user import User
from app.schemas.conversation import ConversationCreate, ConversationUpdate


class CRUDConversation(CRUDBase[Conversation, ConversationCreate, ConversationUpdate]):
    def get_direct_conversation(
        self, session: Session, *, user1_id: uuid.UUID, user2_id: uuid.UUID
    ) -> Conversation | None:
        """Find existing direct conversation between two specific users."""
        # Get all direct conversations for user1
        user1_convs = (
            select(Conversation.id)
            .join(ConversationMember)
            .where(
                ConversationMember.user_id == user1_id,
                Conversation.type == "direct",
                Conversation.member_count == 2,  # Only direct conversations with exactly 2 members
            )
        )
        
        # Find conversations where both users are members
        statement = (
            select(Conversation)
            .join(ConversationMember)
            .where(
                ConversationMember.user_id == user2_id,
                Conversation.id.in_(user1_convs),
                Conversation.type == "direct",
            )
        )
        
        return session.exec(statement).first()

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

    def get_conversation_members_with_users(
        self, session: Session, *, conversation_id: uuid.UUID
    ) -> list[ConversationMember]:
        """Get conversation members with user information loaded."""
        statement = (
            select(ConversationMember)
            .join(User, ConversationMember.user_id == User.id)
            .where(ConversationMember.conversation_id == conversation_id)
        )
        members = list(session.exec(statement).all())
        
        # Manually load the user relationship for each member
        for member in members:
            member.user = session.get(User, member.user_id)
        
        return members


# Create instances
conversation = CRUDConversation(Conversation)
conversation_member = CRUDConversationMember(ConversationMember)

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON
from sqlmodel import Field, Relationship, SQLModel

from app.schemas.conversation import ConversationBase, ConversationMemberBase

if TYPE_CHECKING:
    from app.models.message import Message
    from app.models.user import User


class Conversation(ConversationBase, table=True):
    """Conversation database model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    creator_id: uuid.UUID = Field(foreign_key="user.id")
    member_count: int = Field(default=0)
    last_message_id: Optional[uuid.UUID] = Field(default=None, foreign_key="message.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    creator: "User" = Relationship(back_populates="owned_conversations")
    members: list["ConversationMember"] = Relationship(
        back_populates="conversation", cascade_delete=True
    )
    messages: list["Message"] = Relationship(
        back_populates="conversation", cascade_delete=True
    )
    last_message: Optional["Message"] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[Conversation.last_message_id]",
            "post_update": True,
        }
    )
    settings: list["ConversationSettings"] = Relationship(
        back_populates="conversation", cascade_delete=True
    )


class ConversationMember(ConversationMemberBase, table=True):
    """Conversation member database model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id")
    user_id: uuid.UUID = Field(foreign_key="user.id")
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    left_at: Optional[datetime] = Field(default=None)
    unread_count: int = Field(default=0)
    last_read_message_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="message.id"
    )
    last_read_at: Optional[datetime] = Field(default=None)
    last_important_message_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="message.id"
    )

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="members")
    user: "User" = Relationship(back_populates="conversation_memberships")
    last_read_message: Optional["Message"] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[ConversationMember.last_read_message_id]"
        }
    )
    last_important_message: Optional["Message"] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[ConversationMember.last_important_message_id]"
        }
    )


class ConversationSettings(SQLModel, table=True):
    """Conversation settings key-value store"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id")
    key: str = Field(max_length=128)
    value: dict = Field(default_factory=dict, sa_type=JSON)

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="settings")

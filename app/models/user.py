import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON
from sqlmodel import Field, Relationship, SQLModel

from app.schemas.user import UserBase

if TYPE_CHECKING:
    from app.models.contact import Contact
    from app.models.conversation import Conversation, ConversationMember
    from app.models.device import Device
    from app.models.item import Item
    from app.models.message import Message


class User(UserBase, table=True):
    """User database model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    normalized_username: str = Field(max_length=64, unique=True, index=True)
    password_hash: str = Field(max_length=255)
    salt: str = Field(max_length=128)
    user_metadata: Optional[dict] = Field(default=None, sa_type=JSON)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    deleted_at: Optional[datetime] = Field(default=None)

    # Relationships
    devices: list["Device"] = Relationship(back_populates="user", cascade_delete=True)
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    sent_messages: list["Message"] = Relationship(
        back_populates="sender", cascade_delete=True
    )
    conversation_memberships: list["ConversationMember"] = Relationship(
        back_populates="user", cascade_delete=True
    )
    owned_conversations: list["Conversation"] = Relationship(
        back_populates="creator", cascade_delete=True
    )
    contacts: list["Contact"] = Relationship(
        back_populates="owner", cascade_delete=True
    )


class UserProfile(SQLModel, table=True):
    """User profile for extended metadata"""

    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    profile_json: dict = Field(default_factory=dict, sa_type=JSON)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

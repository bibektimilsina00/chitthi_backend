import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON
from sqlmodel import Field, SQLModel


# Shared properties
class ConversationBase(SQLModel):
    type: str = Field(default="direct", max_length=16)
    title: Optional[str] = Field(default=None, max_length=255)
    topic: Optional[str] = Field(default=None, max_length=255)
    avatar_url: Optional[str] = Field(default=None)
    visibility: str = Field(default="members", max_length=16)
    archived: bool = Field(default=False)
    conv_metadata: Optional[dict] = Field(default=None, sa_type=JSON)


# Properties to receive via API on creation
class ConversationCreate(ConversationBase):
    pass


# Properties to receive via API on update
class ConversationUpdate(SQLModel):
    title: Optional[str] = Field(default=None, max_length=255)
    topic: Optional[str] = Field(default=None, max_length=255)
    avatar_url: Optional[str] = Field(default=None)
    visibility: Optional[str] = Field(default=None, max_length=16)
    archived: Optional[bool] = Field(default=None)
    conv_metadata: Optional[dict] = Field(default=None, sa_type=JSON)


# Properties to return via API
class ConversationPublic(ConversationBase):
    id: uuid.UUID
    creator_id: uuid.UUID
    member_count: int
    last_message_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ConversationsPublic(SQLModel):
    data: list[ConversationPublic]
    count: int


# Conversation member schemas
class ConversationMemberBase(SQLModel):
    role: str = Field(default="member", max_length=16)
    is_muted: bool = Field(default=False)


class ConversationMemberCreate(ConversationMemberBase):
    user_id: uuid.UUID


class ConversationMemberUpdate(SQLModel):
    role: Optional[str] = Field(default=None, max_length=16)
    is_muted: Optional[bool] = Field(default=None)


class ConversationMemberPublic(ConversationMemberBase):
    id: uuid.UUID
    conversation_id: uuid.UUID
    user_id: uuid.UUID
    joined_at: datetime
    left_at: Optional[datetime] = None
    unread_count: int
    last_read_message_id: Optional[uuid.UUID] = None
    last_read_at: Optional[datetime] = None
    last_important_message_id: Optional[uuid.UUID] = None

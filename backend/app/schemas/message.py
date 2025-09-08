import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON
from sqlmodel import Field, SQLModel


# Shared properties
class MessageBase(SQLModel):
    ciphertext: str  # Base64 AEAD ciphertext
    ciphertext_nonce: str = Field(max_length=128)
    encryption_algo: str = Field(default="xchacha20_poly1305", max_length=64)
    sender_ephemeral_pub: Optional[str] = Field(default=None)
    signature: Optional[str] = Field(default=None)
    message_type: str = Field(default="text", max_length=32)
    preview_text_hash: Optional[str] = Field(default=None, max_length=128)
    is_edited: bool = Field(default=False)
    edit_history: Optional[list[dict]] = Field(default=None, sa_type=JSON)
    is_deleted: bool = Field(default=False)
    send_status: str = Field(default="queued", max_length=32)
    msg_metadata: Optional[dict] = Field(default=None, sa_type=JSON)


# Properties to receive via API on creation
class MessageCreate(MessageBase):
    conversation_id: uuid.UUID


# Properties to receive via API on update
class MessageUpdate(SQLModel):
    ciphertext: Optional[str] = Field(default=None)
    message_type: Optional[str] = Field(default=None, max_length=32)
    is_edited: Optional[bool] = Field(default=None)
    edit_history: Optional[dict] = Field(default=None, sa_type=JSON)
    send_status: Optional[str] = Field(default=None, max_length=32)
    msg_metadata: Optional[dict] = Field(default=None, sa_type=JSON)


# Properties to return via API
class MessagePublic(MessageBase):
    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


class MessagesPublic(SQLModel):
    data: list[MessagePublic]
    count: int


# Message attachment schemas
class MessageAttachmentBase(SQLModel):
    encrypted: bool = Field(default=True)
    file_name_enc: Optional[str] = Field(default=None, max_length=255)
    file_size: Optional[int] = Field(default=None)
    mime_type: Optional[str] = Field(default=None, max_length=128)
    width: Optional[int] = Field(default=None)
    height: Optional[int] = Field(default=None)
    duration_seconds: Optional[int] = Field(default=None)
    checksum: Optional[str] = Field(default=None, max_length=128)
    encryption_meta: Optional[dict] = Field(default=None, sa_type=JSON)


class MessageAttachmentCreate(MessageAttachmentBase):
    message_id: uuid.UUID
    storage_id: uuid.UUID


class MessageAttachmentPublic(MessageAttachmentBase):
    id: uuid.UUID
    message_id: uuid.UUID
    storage_id: uuid.UUID
    created_at: datetime


# Message status schemas
class MessageStatusBase(SQLModel):
    status: str = Field(default="sent", max_length=32)
    platform: Optional[str] = Field(default=None, max_length=32)


class MessageStatusCreate(MessageStatusBase):
    message_id: uuid.UUID
    user_id: uuid.UUID
    device_id: Optional[uuid.UUID] = None


class MessageStatusPublic(MessageStatusBase):
    id: uuid.UUID
    message_id: uuid.UUID
    user_id: uuid.UUID
    device_id: Optional[uuid.UUID] = None
    status_at: datetime
    created_at: datetime


# Reactions schemas
class MessageReactionBase(SQLModel):
    reaction: str = Field(max_length=64)


class MessageReactionCreate(MessageReactionBase):
    message_id: uuid.UUID


class MessageReactionPublic(MessageReactionBase):
    id: uuid.UUID
    message_id: uuid.UUID
    user_id: uuid.UUID
    reacted_at: datetime

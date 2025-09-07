import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON
from sqlmodel import Field, Relationship, SQLModel

from app.schemas.message import (
    MessageAttachmentBase,
    MessageBase,
    MessageReactionBase,
    MessageStatusBase,
)

if TYPE_CHECKING:
    from app.models.conversation import Conversation
    from app.models.device import Device
    from app.models.media import MediaStore
    from app.models.user import User


class Message(MessageBase, table=True):
    """Message database model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id")
    sender_id: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    deleted_at: Optional[datetime] = Field(default=None)

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
    sender: "User" = Relationship(back_populates="sent_messages")
    participants_cache: Optional["MessageParticipantsCache"] = Relationship(
        back_populates="message", cascade_delete=True
    )
    encrypted_keys: list["MessageEncryptedKeys"] = Relationship(
        back_populates="message", cascade_delete=True
    )
    attachments: list["MessageAttachment"] = Relationship(
        back_populates="message", cascade_delete=True
    )
    statuses: list["MessageStatus"] = Relationship(
        back_populates="message", cascade_delete=True
    )
    reactions: list["MessageReaction"] = Relationship(
        back_populates="message", cascade_delete=True
    )


class MessageParticipantsCache(SQLModel, table=True):
    """Cache for message participants for quick lookups"""

    message_id: uuid.UUID = Field(foreign_key="message.id", primary_key=True)
    participant_ids: list[str] = Field(
        default_factory=list, sa_type=JSON
    )  # Array of participant UUIDs
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    message: "Message" = Relationship(back_populates="participants_cache")


class MessageEncryptedKeys(SQLModel, table=True):
    """Per-recipient encrypted CEKs"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    message_id: uuid.UUID = Field(foreign_key="message.id")
    recipient_user_id: uuid.UUID = Field(foreign_key="user.id")
    recipient_device_id: uuid.UUID = Field(foreign_key="device.id")
    encrypted_key: str
    key_algo: str = Field(default="x25519-aead", max_length=64)
    nonce: str = Field(max_length=128)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    message: "Message" = Relationship(back_populates="encrypted_keys")
    recipient_user: "User" = Relationship()
    recipient_device: "Device" = Relationship()


class MessageAttachment(MessageAttachmentBase, table=True):
    """Message attachment database model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    message_id: uuid.UUID = Field(foreign_key="message.id")
    storage_id: uuid.UUID = Field(foreign_key="mediastore.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    message: "Message" = Relationship(back_populates="attachments")
    storage: "MediaStore" = Relationship()


class MessageStatus(MessageStatusBase, table=True):
    """Message delivery and read status"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    message_id: uuid.UUID = Field(foreign_key="message.id")
    user_id: uuid.UUID = Field(foreign_key="user.id")
    device_id: Optional[uuid.UUID] = Field(default=None, foreign_key="device.id")
    status_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    message: "Message" = Relationship(back_populates="statuses")
    user: "User" = Relationship()
    device: Optional["Device"] = Relationship()


class MessageReaction(MessageReactionBase, table=True):
    """Message reactions"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    message_id: uuid.UUID = Field(foreign_key="message.id")
    user_id: uuid.UUID = Field(foreign_key="user.id")
    reacted_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    message: "Message" = Relationship(back_populates="reactions")
    user: "User" = Relationship()


class ReadReceiptsSummary(SQLModel, table=True):
    """Summary of read receipts for messages"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id")
    message_id: uuid.UUID = Field(foreign_key="message.id")
    delivered_count: int = Field(default=0)
    seen_count: int = Field(default=0)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    conversation: "Conversation" = Relationship()
    message: "Message" = Relationship()


class PinnedItems(SQLModel, table=True):
    """Pinned messages in conversations"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id")
    message_id: uuid.UUID = Field(foreign_key="message.id")
    pinned_by: uuid.UUID = Field(foreign_key="user.id")
    pinned_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None)

    # Relationships
    conversation: "Conversation" = Relationship()
    message: "Message" = Relationship()
    pinned_by_user: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[PinnedItems.pinned_by]"}
    )


class StarredMessages(SQLModel, table=True):
    """User's starred messages"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    message_id: uuid.UUID = Field(foreign_key="message.id")
    starred_at: datetime = Field(default_factory=datetime.utcnow)


class MessageEditHistory(SQLModel, table=True):
    """History of message edits"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    message_id: uuid.UUID = Field(foreign_key="message.id")
    editor_id: uuid.UUID = Field(foreign_key="user.id")
    previous_body_hash: str = Field(max_length=128)
    previous_ciphertext: str
    edited_at: datetime = Field(default_factory=datetime.utcnow)


class MessageDrafts(SQLModel, table=True):
    """User's message drafts"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id")
    draft_text_enc: str
    attachments: Optional[dict] = Field(default=None, sa_type=JSON)
    updated_at: Optional[datetime] = Field(default=None)

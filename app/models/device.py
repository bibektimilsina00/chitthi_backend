import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.schemas.device import DeviceBase

if TYPE_CHECKING:
    from app.models.auth import RefreshToken, UserSession
    from app.models.crypto import DeviceKeys
    from app.models.message import MessageEncryptedKeys, MessageStatus
    from app.models.user import User


class Device(DeviceBase, table=True):
    """Device database model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    last_seen: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="devices")
    device_keys: list["DeviceKeys"] = Relationship(
        back_populates="device", cascade_delete=True
    )
    refresh_tokens: list["RefreshToken"] = Relationship(
        back_populates="device", cascade_delete=True
    )
    user_sessions: list["UserSession"] = Relationship(
        back_populates="device", cascade_delete=True
    )
    message_encrypted_keys: list["MessageEncryptedKeys"] = Relationship(
        cascade_delete=True
    )
    message_statuses: list["MessageStatus"] = Relationship(cascade_delete=True)

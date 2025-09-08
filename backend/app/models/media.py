import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.schemas.media import MediaStoreBase, PushNotificationBase

if TYPE_CHECKING:
    from app.models.device import Device
    from app.models.message import MessageAttachment
    from app.models.user import User


class MediaStore(MediaStoreBase, table=True):
    """Media storage database model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    attachments: list["MessageAttachment"] = Relationship(back_populates="storage")


class PushNotifications(PushNotificationBase, table=True):
    """Push notifications database model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    device_id: uuid.UUID = Field(foreign_key="device.id")
    sent_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship()
    device: "Device" = Relationship()

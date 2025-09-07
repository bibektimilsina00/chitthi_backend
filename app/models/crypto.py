import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.schemas.crypto import (
    DeviceKeyBase,
    IdentityKeyBase,
    KeyBackupBase,
    OneTimePrekeyBase,
)

if TYPE_CHECKING:
    from app.models.device import Device
    from app.models.user import User


class IdentityKeys(IdentityKeyBase, table=True):
    """Identity keys for E2EE"""

    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    signed_prekey_created: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: "User" = Relationship()


class OneTimePrekeys(OneTimePrekeyBase, table=True):
    """One-time prekeys for E2EE key exchange"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    used_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: "User" = Relationship()


class DeviceKeys(DeviceKeyBase, table=True):
    """Device-specific keys for E2EE"""

    device_id: uuid.UUID = Field(foreign_key="device.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    revoked_at: Optional[datetime] = Field(default=None)

    # Relationships
    device: "Device" = Relationship(back_populates="device_keys")


class KeyBackups(KeyBackupBase, table=True):
    """Encrypted key backups"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship()
    updated_at: Optional[datetime] = Field(default=None)

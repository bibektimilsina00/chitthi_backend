import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.schemas.auth import OAuthProviderBase, RefreshTokenBase, UserSessionBase

if TYPE_CHECKING:
    from app.models.device import Device
    from app.models.user import User


class UserSession(UserSessionBase, table=True):
    """User session database model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    device_id: uuid.UUID = Field(foreign_key="device.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_seen: Optional[datetime] = Field(default=None)
    expires_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: "User" = Relationship()
    device: "Device" = Relationship(back_populates="user_sessions")


class RefreshToken(RefreshTokenBase, table=True):
    """Refresh token database model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    device_id: uuid.UUID = Field(foreign_key="device.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    revoked_at: Optional[datetime] = Field(default=None)
    expires_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: "User" = Relationship()
    device: "Device" = Relationship(back_populates="refresh_tokens")


class OAuthProvider(OAuthProviderBase, table=True):
    """OAuth provider database model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship()

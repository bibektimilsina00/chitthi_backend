import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON
from sqlmodel import Field, SQLModel


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# Session schemas
class UserSessionBase(SQLModel):
    session_token: str = Field(max_length=255, unique=True)
    ip: Optional[str] = Field(default=None, max_length=64)
    user_agent: Optional[str] = Field(default=None)
    revoked: bool = Field(default=False)


class UserSessionCreate(UserSessionBase):
    user_id: uuid.UUID
    device_id: uuid.UUID


class UserSessionUpdate(SQLModel):
    revoked: Optional[bool] = Field(default=None)


class UserSessionPublic(UserSessionBase):
    id: uuid.UUID
    user_id: uuid.UUID
    device_id: uuid.UUID
    created_at: datetime
    last_seen: Optional[datetime] = None
    expires_at: Optional[datetime] = None


# Refresh token schemas
class RefreshTokenBase(SQLModel):
    token_hash: str = Field(max_length=255)


class RefreshTokenCreate(RefreshTokenBase):
    user_id: uuid.UUID
    device_id: uuid.UUID


class RefreshTokenPublic(RefreshTokenBase):
    id: uuid.UUID
    user_id: uuid.UUID
    device_id: uuid.UUID
    created_at: datetime
    revoked_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


# OAuth provider schemas
class OAuthProviderBase(SQLModel):
    provider: str = Field(max_length=64)
    provider_user_id: str = Field(max_length=255)
    raw_profile: Optional[dict] = Field(default=None, sa_type=JSON)


class OAuthProviderCreate(OAuthProviderBase):
    user_id: uuid.UUID


class OAuthProviderPublic(OAuthProviderBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime

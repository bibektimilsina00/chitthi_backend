import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON
from sqlmodel import Field, SQLModel


# Shared properties
class DeviceBase(SQLModel):
    device_id: str = Field(max_length=255)
    device_name: Optional[str] = Field(default=None, max_length=128)
    platform: Optional[str] = Field(default=None, max_length=32)
    push_token: Optional[str] = Field(default=None)
    app_version: Optional[str] = Field(default=None, max_length=64)
    revoked: bool = Field(default=False)


# Properties to receive via API on creation
class DeviceCreate(DeviceBase):
    pass


# Properties to receive via API on update
class DeviceUpdate(SQLModel):
    device_name: Optional[str] = Field(default=None, max_length=128)
    push_token: Optional[str] = Field(default=None)
    app_version: Optional[str] = Field(default=None, max_length=64)
    revoked: Optional[bool] = Field(default=None)


# Properties to return via API
class DevicePublic(DeviceBase):
    id: uuid.UUID
    user_id: uuid.UUID
    last_seen: Optional[datetime] = None
    created_at: datetime


class DevicesPublic(SQLModel):
    data: list[DevicePublic]
    count: int

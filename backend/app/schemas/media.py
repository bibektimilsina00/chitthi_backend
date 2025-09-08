import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON
from sqlmodel import Field, SQLModel


# Media store schemas
class MediaStoreBase(SQLModel):
    user_id: uuid.UUID = Field(foreign_key="user.id")
    filename: str = Field(max_length=255)
    original_filename: Optional[str] = Field(default=None, max_length=255)
    file_size: int
    file_type: str = Field(max_length=100)
    storage_path: str = Field(max_length=500)
    provider: Optional[str] = Field(default="local", max_length=64)
    bucket: Optional[str] = Field(default=None, max_length=255)
    object_key: Optional[str] = Field(default=None)
    url: Optional[str] = Field(default=None)
    storage_class: Optional[str] = Field(default=None, max_length=64)
    media_metadata: Optional[dict] = Field(default=None, sa_type=JSON)
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default=None)


class MediaStoreCreate(MediaStoreBase):
    pass


class MediaStoreUpdate(SQLModel):
    filename: Optional[str] = Field(default=None, max_length=255)
    url: Optional[str] = Field(default=None)
    storage_class: Optional[str] = Field(default=None, max_length=64)
    media_metadata: Optional[dict] = Field(default=None, sa_type=JSON)
    is_deleted: Optional[bool] = Field(default=None)
    deleted_at: Optional[datetime] = Field(default=None)


class MediaStorePublic(MediaStoreBase):
    id: uuid.UUID
    created_at: datetime


class MediaStoresPublic(SQLModel):
    data: list[MediaStorePublic]
    count: int


# Push notification schemas
class PushNotificationBase(SQLModel):
    title: str = Field(max_length=255)
    body: str
    payload: Optional[dict] = Field(default=None, sa_type=JSON)
    provider_response: Optional[dict] = Field(default=None, sa_type=JSON)
    status: str = Field(default="pending", max_length=32)
    retry_count: int = Field(default=0)


class PushNotificationCreate(PushNotificationBase):
    user_id: uuid.UUID
    device_id: uuid.UUID


class PushNotificationPublic(PushNotificationBase):
    id: uuid.UUID
    user_id: uuid.UUID
    device_id: uuid.UUID
    sent_at: Optional[datetime] = None
    created_at: datetime

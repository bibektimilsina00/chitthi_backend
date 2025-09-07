import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON
from sqlmodel import Field, SQLModel


# Contact schemas
class ContactBase(SQLModel):
    alias: Optional[str] = Field(default=None, max_length=128)
    is_blocked: bool = Field(default=False)
    is_favorite: bool = Field(default=False)


class ContactCreate(ContactBase):
    contact_user_id: uuid.UUID


class ContactUpdate(ContactBase):
    pass


class ContactPublic(ContactBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    contact_user_id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None


class ContactsPublic(SQLModel):
    data: list[ContactPublic]
    count: int


# Block schemas
class BlockBase(SQLModel):
    reason: Optional[str] = Field(default=None, max_length=256)


class BlockCreate(BlockBase):
    blocked_id: uuid.UUID


class BlockPublic(BlockBase):
    id: uuid.UUID
    blocker_id: uuid.UUID
    blocked_id: uuid.UUID
    created_at: datetime


# Contact Permission schemas
class ContactPermissionBase(SQLModel):
    can_see_online_status: bool = Field(default=True)
    can_see_profile_photo: bool = Field(default=True)
    can_see_last_seen: bool = Field(default=True)
    can_add_to_groups: bool = Field(default=True)
    can_call: bool = Field(default=True)


class ContactPermissionCreate(ContactPermissionBase):
    user_id: uuid.UUID
    contact_user_id: uuid.UUID


class ContactPermissionUpdate(ContactPermissionBase):
    pass


class ContactPermissionPublic(ContactPermissionBase):
    id: uuid.UUID
    user_id: uuid.UUID
    contact_user_id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None


class BlocksPublic(SQLModel):
    data: list[BlockPublic]
    count: int

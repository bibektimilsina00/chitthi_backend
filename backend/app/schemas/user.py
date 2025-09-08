import uuid
from datetime import datetime
from typing import Optional

from pydantic import EmailStr
from sqlalchemy import JSON
from sqlmodel import Field, SQLModel


# Shared properties for users
class UserBase(SQLModel):
    username: str = Field(max_length=64, unique=True, index=True)
    email: Optional[EmailStr] = Field(default=None, max_length=255, unique=True)
    phone: Optional[str] = Field(default=None, max_length=32, unique=True)
    display_name: Optional[str] = Field(default=None, max_length=128)
    about: Optional[str] = Field(default=None)
    avatar_url: Optional[str] = Field(default=None)
    locale: Optional[str] = Field(default=None, max_length=16)
    timezone: Optional[str] = Field(default=None, max_length=64)
    is_active: bool = Field(default=True)
    is_bot: bool = Field(default=False)
    is_superuser: bool = Field(default=False)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    username: str = Field(max_length=64)
    email: Optional[EmailStr] = Field(default=None, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    display_name: Optional[str] = Field(default=None, max_length=128)


# Properties to receive via API on update, all are optional
class UserUpdate(SQLModel):
    username: Optional[str] = Field(default=None, max_length=64)
    email: Optional[EmailStr] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=32)
    display_name: Optional[str] = Field(default=None, max_length=128)
    about: Optional[str] = Field(default=None)
    avatar_url: Optional[str] = Field(default=None)
    locale: Optional[str] = Field(default=None, max_length=16)
    timezone: Optional[str] = Field(default=None, max_length=64)
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    display_name: Optional[str] = Field(default=None, max_length=128)
    about: Optional[str] = Field(default=None)
    avatar_url: Optional[str] = Field(default=None)
    locale: Optional[str] = Field(default=None, max_length=16)
    timezone: Optional[str] = Field(default=None, max_length=64)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    normalized_username: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# User profile schema
class UserProfileBase(SQLModel):
    profile_json: Optional[dict] = Field(default=None, sa_type=JSON)


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfilePublic(UserProfileBase):
    user_id: uuid.UUID
    updated_at: Optional[datetime] = None

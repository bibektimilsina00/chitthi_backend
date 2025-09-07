import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON
from sqlmodel import Field, SQLModel


# Identity key schemas
class IdentityKeyBase(SQLModel):
    identity_pubkey: str
    identity_algo: str = Field(default="ed25519", max_length=64)
    signed_prekey_id: int
    signed_prekey_pub: str
    signed_prekey_sig: str
    prekey_count: int = Field(default=0)
    crypto_metadata: Optional[dict] = Field(default=None, sa_type=JSON)


class IdentityKeyCreate(IdentityKeyBase):
    pass


class IdentityKeyUpdate(SQLModel):
    signed_prekey_id: Optional[int] = Field(default=None)
    signed_prekey_pub: Optional[str] = Field(default=None)
    signed_prekey_sig: Optional[str] = Field(default=None)
    prekey_count: Optional[int] = Field(default=None)
    crypto_metadata: Optional[dict] = Field(default=None, sa_type=JSON)


class IdentityKeyPublic(IdentityKeyBase):
    user_id: uuid.UUID
    signed_prekey_created: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None


# One-time prekey schemas
class OneTimePrekeyBase(SQLModel):
    prekey_id: int
    prekey_pub: str
    used: bool = Field(default=False)


class OneTimePrekeyCreate(OneTimePrekeyBase):
    user_id: uuid.UUID


class OneTimePrekeyPublic(OneTimePrekeyBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    used_at: Optional[datetime] = None


# Device key schemas
class DeviceKeyBase(SQLModel):
    device_pubkey: str
    key_algo: str = Field(default="x25519", max_length=64)
    signed_by_identity: str


class DeviceKeyCreate(DeviceKeyBase):
    device_id: uuid.UUID


class DeviceKeyPublic(DeviceKeyBase):
    device_id: uuid.UUID
    created_at: datetime
    revoked_at: Optional[datetime] = None


# Key backup schemas
class KeyBackupBase(SQLModel):
    backup_blob: str
    version: str = Field(max_length=64)


class KeyBackupCreate(KeyBackupBase):
    user_id: uuid.UUID


class KeyBackupPublic(KeyBackupBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

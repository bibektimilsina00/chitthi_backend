import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlmodel import Session, desc, select

from app.crud.base import CRUDBase
from app.models.crypto import DeviceKeys, IdentityKeys, KeyBackups, OneTimePrekeys
from app.schemas.crypto import (
    DeviceKeyCreate,
    IdentityKeyCreate,
    IdentityKeyUpdate,
    KeyBackupCreate,
    OneTimePrekeyCreate,
)


class CRUDIdentityKeys(CRUDBase[IdentityKeys, IdentityKeyCreate, IdentityKeyUpdate]):
    def get_by_user_id(
        self, session: Session, *, user_id: uuid.UUID
    ) -> IdentityKeys | None:
        """Get identity keys for a user."""
        return session.get(IdentityKeys, user_id)

    def update_signed_prekey(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        signed_prekey_id: int,
        signed_prekey_pub: str,
        signed_prekey_sig: str,
    ) -> IdentityKeys | None:
        """Update signed prekey for a user."""
        identity_keys = session.get(IdentityKeys, user_id)
        if identity_keys:
            identity_keys.signed_prekey_id = signed_prekey_id
            identity_keys.signed_prekey_pub = signed_prekey_pub
            identity_keys.signed_prekey_sig = signed_prekey_sig
            identity_keys.signed_prekey_created = datetime.utcnow()
            identity_keys.updated_at = datetime.utcnow()
            session.add(identity_keys)
            session.commit()
            session.refresh(identity_keys)
            return identity_keys
        return None

    def increment_prekey_count(
        self, session: Session, *, user_id: uuid.UUID, count: int = 1
    ) -> IdentityKeys | None:
        """Increment prekey count for a user."""
        identity_keys = session.get(IdentityKeys, user_id)
        if identity_keys:
            identity_keys.prekey_count += count
            identity_keys.updated_at = datetime.utcnow()
            session.add(identity_keys)
            session.commit()
            session.refresh(identity_keys)
            return identity_keys
        return None


class CRUDOneTimePrekeys(CRUDBase[OneTimePrekeys, OneTimePrekeyCreate, Any]):
    def get_available_prekeys(
        self, session: Session, *, user_id: uuid.UUID, limit: int = 10
    ) -> list[OneTimePrekeys]:
        """Get available (unused) prekeys for a user."""
        statement = (
            select(OneTimePrekeys)
            .where(OneTimePrekeys.user_id == user_id, OneTimePrekeys.used == False)
            .limit(limit)
        )
        return list(session.exec(statement).all())

    def get_by_user_and_prekey_id(
        self, session: Session, *, user_id: uuid.UUID, prekey_id: int
    ) -> OneTimePrekeys | None:
        """Get a specific prekey by user and prekey ID."""
        statement = select(OneTimePrekeys).where(
            OneTimePrekeys.user_id == user_id,
            OneTimePrekeys.prekey_id == prekey_id,
        )
        return session.exec(statement).first()

    def mark_as_used(
        self, session: Session, *, prekey_id: uuid.UUID
    ) -> OneTimePrekeys | None:
        """Mark a prekey as used."""
        prekey = session.get(OneTimePrekeys, prekey_id)
        if prekey and not prekey.used:
            prekey.used = True
            prekey.used_at = datetime.utcnow()
            session.add(prekey)
            session.commit()
            session.refresh(prekey)
            return prekey
        return None

    def cleanup_used_prekeys(
        self, session: Session, *, user_id: uuid.UUID, days_old: int = 30
    ) -> int:
        """Clean up old used prekeys."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        statement = select(OneTimePrekeys).where(
            OneTimePrekeys.user_id == user_id,
            OneTimePrekeys.used == True,
            OneTimePrekeys.used_at != None,
        )

        prekeys = session.exec(statement).all()
        count = 0
        for prekey in prekeys:
            if prekey.used_at and prekey.used_at < cutoff_date:
                session.delete(prekey)
                count += 1

        session.commit()
        return count

    def count_available_prekeys(self, session: Session, *, user_id: uuid.UUID) -> int:
        """Count available prekeys for a user."""
        statement = select(OneTimePrekeys).where(
            OneTimePrekeys.user_id == user_id, OneTimePrekeys.used == False
        )
        return len(list(session.exec(statement).all()))


class CRUDDeviceKeys(CRUDBase[DeviceKeys, DeviceKeyCreate, Any]):
    def get_by_device_id(
        self, session: Session, *, device_id: uuid.UUID
    ) -> DeviceKeys | None:
        """Get device keys by device ID."""
        return session.get(DeviceKeys, device_id)

    def revoke_device_keys(
        self, session: Session, *, device_id: uuid.UUID
    ) -> DeviceKeys | None:
        """Revoke device keys."""
        device_keys = session.get(DeviceKeys, device_id)
        if device_keys:
            device_keys.revoked_at = datetime.utcnow()
            session.add(device_keys)
            session.commit()
            session.refresh(device_keys)
            return device_keys
        return None

    def get_active_device_keys(
        self, session: Session, *, device_id: uuid.UUID
    ) -> DeviceKeys | None:
        """Get active (non-revoked) device keys."""
        device_keys = session.get(DeviceKeys, device_id)
        if device_keys and device_keys.revoked_at is None:
            return device_keys
        return None


class CRUDKeyBackups(CRUDBase[KeyBackups, KeyBackupCreate, Any]):
    def get_user_backups(
        self, session: Session, *, user_id: uuid.UUID, limit: int = 10
    ) -> list[KeyBackups]:
        """Get key backups for a user."""
        statement = (
            select(KeyBackups)
            .where(KeyBackups.user_id == user_id)
            .order_by(desc(KeyBackups.created_at))
            .limit(limit)
        )
        return list(session.exec(statement).all())

    def get_latest_backup(
        self, session: Session, *, user_id: uuid.UUID, version: str | None = None
    ) -> KeyBackups | None:
        """Get the latest backup for a user, optionally for a specific version."""
        statement = select(KeyBackups).where(KeyBackups.user_id == user_id)
        if version:
            statement = statement.where(KeyBackups.version == version)
        statement = statement.order_by(desc(KeyBackups.created_at))
        return session.exec(statement).first()

    def cleanup_old_backups(
        self, session: Session, *, user_id: uuid.UUID, keep_count: int = 5
    ) -> int:
        """Keep only the latest N backups for a user."""
        backups = self.get_user_backups(session, user_id=user_id, limit=1000)
        if len(backups) <= keep_count:
            return 0

        to_delete = backups[keep_count:]
        count = 0
        for backup in to_delete:
            session.delete(backup)
            count += 1

        session.commit()
        return count


# Create instances
identity_keys = CRUDIdentityKeys(IdentityKeys)
one_time_prekeys = CRUDOneTimePrekeys(OneTimePrekeys)
device_keys = CRUDDeviceKeys(DeviceKeys)
key_backups = CRUDKeyBackups(KeyBackups)

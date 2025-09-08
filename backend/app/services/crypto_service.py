"""Cryptographic service for E2E encryption operations."""

import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session

from app import crud
from app.models.crypto import DeviceKeys, IdentityKeys, OneTimePrekeys
from app.schemas.crypto import DeviceKeyCreate, IdentityKeyCreate, OneTimePrekeyCreate


class CryptoService:
    """Service for handling E2E encryption operations."""

    def initialize_user_crypto(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        identity_pubkey: str,
        signed_prekey_id: int,
        signed_prekey_pub: str,
        signed_prekey_sig: str,
        one_time_prekeys: list[dict[str, Any]],
    ) -> IdentityKeys:
        """Initialize cryptographic materials for a new user."""
        # Create identity keys
        identity_create_data = {
            "user_id": user_id,
            "identity_pubkey": identity_pubkey,
            "signed_prekey_id": signed_prekey_id,
            "signed_prekey_pub": signed_prekey_pub,
            "signed_prekey_sig": signed_prekey_sig,
            "prekey_count": len(one_time_prekeys),
        }

        identity_keys = IdentityKeys(**identity_create_data)
        session.add(identity_keys)
        session.commit()
        session.refresh(identity_keys)

        # Create one-time prekeys
        for prekey_data in one_time_prekeys:
            prekey_create = OneTimePrekeyCreate(
                user_id=user_id,
                prekey_id=prekey_data["prekey_id"],
                prekey_pub=prekey_data["prekey_pub"],
            )
            crud.one_time_prekeys.create(session=session, obj_in=prekey_create)

        return identity_keys

    def register_device_keys(
        self,
        session: Session,
        *,
        device_id: uuid.UUID,
        device_pubkey: str,
        signed_by_identity: str,
        key_algo: str = "x25519",
    ) -> DeviceKeys:
        """Register cryptographic keys for a device."""
        device_key_data = {
            "device_id": device_id,
            "device_pubkey": device_pubkey,
            "signed_by_identity": signed_by_identity,
            "key_algo": key_algo,
        }

        device_keys = DeviceKeys(**device_key_data)
        session.add(device_keys)
        session.commit()
        session.refresh(device_keys)
        return device_keys

    def get_user_identity_keys(
        self, session: Session, *, user_id: uuid.UUID
    ) -> IdentityKeys | None:
        """Get identity keys for a user."""
        return crud.identity_keys.get_by_user_id(session, user_id=user_id)

    def get_device_keys(
        self, session: Session, *, device_id: uuid.UUID
    ) -> DeviceKeys | None:
        """Get active device keys."""
        return crud.device_keys.get_active_device_keys(session, device_id=device_id)

    def consume_one_time_prekey(
        self, session: Session, *, user_id: uuid.UUID
    ) -> OneTimePrekeys | None:
        """Get and mark a one-time prekey as used."""
        # Get an available prekey
        available_prekeys = crud.one_time_prekeys.get_available_prekeys(
            session, user_id=user_id, limit=1
        )

        if not available_prekeys:
            return None

        prekey = available_prekeys[0]

        # Mark as used
        return crud.one_time_prekeys.mark_as_used(session, prekey_id=prekey.id)

    def replenish_prekeys(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        new_prekeys: list[dict[str, Any]],
        threshold: int = 10,
    ) -> int:
        """Replenish one-time prekeys if below threshold."""
        # Check current count
        current_count = crud.one_time_prekeys.count_available_prekeys(
            session, user_id=user_id
        )

        if current_count >= threshold:
            return 0

        # Add new prekeys
        created_count = 0
        for prekey_data in new_prekeys:
            prekey_create = OneTimePrekeyCreate(
                user_id=user_id,
                prekey_id=prekey_data["prekey_id"],
                prekey_pub=prekey_data["prekey_pub"],
            )
            crud.one_time_prekeys.create(session=session, obj_in=prekey_create)
            created_count += 1

        # Update prekey count in identity keys
        crud.identity_keys.increment_prekey_count(
            session, user_id=user_id, count=created_count
        )

        return created_count

    def rotate_signed_prekey(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        new_signed_prekey_id: int,
        new_signed_prekey_pub: str,
        new_signed_prekey_sig: str,
    ) -> IdentityKeys | None:
        """Rotate the signed prekey for a user."""
        return crud.identity_keys.update_signed_prekey(
            session,
            user_id=user_id,
            signed_prekey_id=new_signed_prekey_id,
            signed_prekey_pub=new_signed_prekey_pub,
            signed_prekey_sig=new_signed_prekey_sig,
        )

    def revoke_device_keys(
        self, session: Session, *, device_id: uuid.UUID
    ) -> DeviceKeys | None:
        """Revoke cryptographic keys for a device."""
        return crud.device_keys.revoke_device_keys(session, device_id=device_id)

    def get_user_key_bundle(
        self, session: Session, *, user_id: uuid.UUID
    ) -> dict[str, Any] | None:
        """Get a complete key bundle for initiating encrypted communication."""
        # Get identity keys
        identity_keys = self.get_user_identity_keys(session, user_id=user_id)
        if not identity_keys:
            return None

        # Get a one-time prekey (but don't consume it yet)
        available_prekeys = crud.one_time_prekeys.get_available_prekeys(
            session, user_id=user_id, limit=1
        )
        one_time_prekey = available_prekeys[0] if available_prekeys else None

        return {
            "user_id": str(user_id),
            "identity_pubkey": identity_keys.identity_pubkey,
            "signed_prekey": {
                "id": identity_keys.signed_prekey_id,
                "pubkey": identity_keys.signed_prekey_pub,
                "signature": identity_keys.signed_prekey_sig,
            },
            "one_time_prekey": (
                {
                    "id": one_time_prekey.prekey_id,
                    "pubkey": one_time_prekey.prekey_pub,
                }
                if one_time_prekey
                else None
            ),
        }

    def cleanup_old_keys(
        self, session: Session, *, days_old: int = 30
    ) -> dict[str, int]:
        """Clean up old used prekeys."""
        users = crud.user.get_multi(session, limit=1000)  # Get all users

        total_cleaned = 0
        for user in users:
            cleaned = crud.one_time_prekeys.cleanup_used_prekeys(
                session, user_id=user.id, days_old=days_old
            )
            total_cleaned += cleaned

        return {
            "prekeys_cleaned": total_cleaned,
        }


crypto_service = CryptoService()

"""Device management service."""

import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlmodel import Session

from app import crud
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate


class DeviceService:
    """Service for managing user devices."""

    def register_device(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        device_id: str,
        device_name: str | None = None,
        platform: str | None = None,
        push_token: str | None = None,
        app_version: str | None = None,
    ) -> Device:
        """Register a new device for a user."""
        # Check if device with same device_id already exists for this user
        existing_device = crud.device.get_by_device_id(
            session, user_id=user_id, device_id=device_id
        )

        if existing_device:
            # Update existing device
            device_update = DeviceUpdate(
                device_name=device_name,
                push_token=push_token,
                app_version=app_version,
                revoked=False,
            )
            device = crud.device.update(
                session=session, db_obj=existing_device, obj_in=device_update
            )
            # Update last_seen
            device.last_seen = datetime.utcnow()
            session.add(device)
            session.commit()
            session.refresh(device)
            return device

        # Create new device
        device_create_data = {
            "user_id": user_id,
            "device_id": device_id,
            "device_name": device_name,
            "platform": platform,
            "push_token": push_token,
            "app_version": app_version,
        }

        device = Device(**device_create_data)
        device.last_seen = datetime.utcnow()
        session.add(device)
        session.commit()
        session.refresh(device)

        return device

    def update_device(
        self,
        session: Session,
        *,
        device_id: uuid.UUID,
        user_id: uuid.UUID,
        updates: dict[str, Any],
    ) -> Device:
        """Update device information."""
        device = crud.device.get(session, id=device_id)

        if not device or device.user_id != user_id:
            raise ValueError("Device not found")

        device_update = DeviceUpdate(**updates)
        device = crud.device.update(
            session=session, db_obj=device, obj_in=device_update
        )

        # Update last_seen
        device.last_seen = datetime.utcnow()
        session.add(device)
        session.commit()
        session.refresh(device)

        return device

    def revoke_device(
        self, session: Session, *, device_id: uuid.UUID, user_id: uuid.UUID
    ) -> Device:
        """Revoke a device."""
        device = crud.device.get(session, id=device_id)

        if not device or device.user_id != user_id:
            raise ValueError("Device not found")

        device.revoked = True
        session.add(device)
        session.commit()
        session.refresh(device)

        return device

    def get_user_devices(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        include_revoked: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Device]:
        """Get user's devices."""
        return crud.device.get_user_devices(
            session, user_id=user_id, include_revoked=include_revoked
        )

    def update_device_activity(
        self, session: Session, *, device_id: uuid.UUID, user_id: uuid.UUID
    ) -> Device:
        """Update device last seen activity."""
        device = crud.device.get(session, id=device_id)

        if not device or device.user_id != user_id:
            raise ValueError("Device not found")

        device.last_seen = datetime.utcnow()
        session.add(device)
        session.commit()
        session.refresh(device)

        return device

    def get_device_by_device_id(
        self, session: Session, *, device_id: str, user_id: uuid.UUID
    ) -> Device | None:
        """Get device by device_id string."""
        device = crud.device.get_by_device_id(
            session, user_id=user_id, device_id=device_id
        )

        if device:
            return device

        return None

    def cleanup_revoked_devices(
        self, session: Session, *, days_old: int = 30
    ) -> dict[str, int]:
        """Clean up old revoked devices."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        # Remove old revoked devices functionality would need additional CRUD methods
        # For now, return empty result
        return {
            "devices_deleted": 0,
        }

    def get_device_statistics(
        self, session: Session, *, user_id: uuid.UUID
    ) -> dict[str, Any]:
        """Get device statistics for a user."""
        devices = crud.device.get_user_devices(
            session, user_id=user_id, include_revoked=True
        )

        active_devices = [d for d in devices if not d.revoked]
        platforms = {}

        for device in devices:
            if device.platform:
                platforms[device.platform] = platforms.get(device.platform, 0) + 1

        last_active_device = None
        if devices:
            # Find device with most recent last_seen
            devices_with_last_seen = [d for d in devices if d.last_seen]
            if devices_with_last_seen:
                latest_device = devices_with_last_seen[0]
                for device in devices_with_last_seen[1:]:
                    if device.last_seen and (
                        not latest_device.last_seen
                        or device.last_seen > latest_device.last_seen
                    ):
                        latest_device = device
                last_active_device = latest_device.device_name

        return {
            "total_devices": len(devices),
            "active_devices": len(active_devices),
            "revoked_devices": len(devices) - len(active_devices),
            "platforms": platforms,
            "last_active_device": last_active_device,
        }


device_service = DeviceService()


device_service = DeviceService()

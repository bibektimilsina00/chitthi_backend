import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlmodel import Session, desc, select

from app.crud.base import CRUDBase
from app.models.device import Device
from app.models.media import PushNotifications
from app.schemas.device import DeviceCreate, DeviceUpdate
from app.schemas.media import PushNotificationCreate


class CRUDDevice(CRUDBase[Device, DeviceCreate, DeviceUpdate]):
    def get_user_devices(
        self, session: Session, *, user_id: uuid.UUID, include_revoked: bool = False
    ) -> list[Device]:
        """Get all devices for a user."""
        statement = select(Device).where(Device.user_id == user_id)
        if not include_revoked:
            statement = statement.where(Device.revoked == False)
        statement = statement.order_by(desc(Device.last_seen))
        return list(session.exec(statement).all())

    def get_by_device_id(
        self, session: Session, *, user_id: uuid.UUID, device_id: str
    ) -> Device | None:
        """Get device by user and device ID."""
        statement = select(Device).where(
            Device.user_id == user_id, Device.device_id == device_id
        )
        return session.exec(statement).first()

    def update_last_seen(
        self, session: Session, *, device_id: uuid.UUID
    ) -> Device | None:
        """Update last seen timestamp for a device."""
        device = session.get(Device, device_id)
        if device and not device.revoked:
            device.last_seen = datetime.utcnow()
            session.add(device)
            session.commit()
            session.refresh(device)
            return device
        return None

    def revoke_device(self, session: Session, *, device_id: uuid.UUID) -> Device | None:
        """Revoke a device."""
        device = session.get(Device, device_id)
        if device:
            device.revoked = True
            session.add(device)
            session.commit()
            session.refresh(device)
            return device
        return None

    def update_push_token(
        self, session: Session, *, device_id: uuid.UUID, push_token: str
    ) -> Device | None:
        """Update push token for a device."""
        device = session.get(Device, device_id)
        if device:
            device.push_token = push_token
            device.last_seen = datetime.utcnow()
            session.add(device)
            session.commit()
            session.refresh(device)
            return device
        return None

    def get_devices_with_push_tokens(
        self, session: Session, *, user_id: uuid.UUID
    ) -> list[Device]:
        """Get active devices with push tokens for a user."""
        statement = select(Device).where(
            Device.user_id == user_id,
            Device.revoked == False,
            Device.push_token != None,
            Device.push_token != "",
        )
        return list(session.exec(statement).all())


class CRUDPushNotifications(CRUDBase[PushNotifications, PushNotificationCreate, Any]):
    def get_user_notifications(
        self, session: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[PushNotifications]:
        """Get push notifications for a user."""
        statement = (
            select(PushNotifications)
            .where(PushNotifications.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(desc(PushNotifications.created_at))
        )
        return list(session.exec(statement).all())

    def get_pending_notifications(
        self, session: Session, *, limit: int = 100
    ) -> list[PushNotifications]:
        """Get pending push notifications."""
        statement = (
            select(PushNotifications)
            .where(PushNotifications.status == "pending")
            .limit(limit)
        )
        return list(session.exec(statement).all())

    def update_status(
        self,
        session: Session,
        *,
        notification_id: uuid.UUID,
        status: str,
        provider_response: dict | None = None,
    ) -> PushNotifications | None:
        """Update push notification status."""
        notification = session.get(PushNotifications, notification_id)
        if notification:
            notification.status = status
            if provider_response:
                notification.provider_response = provider_response
            if status in ["sent", "failed"]:
                notification.sent_at = datetime.utcnow()
            session.add(notification)
            session.commit()
            session.refresh(notification)
            return notification
        return None

    def increment_retry_count(
        self, session: Session, *, notification_id: uuid.UUID
    ) -> PushNotifications | None:
        """Increment retry count for a failed notification."""
        notification = session.get(PushNotifications, notification_id)
        if notification:
            notification.retry_count += 1
            session.add(notification)
            session.commit()
            session.refresh(notification)
            return notification
        return None

    def cleanup_old_notifications(self, session: Session, *, days_old: int = 30) -> int:
        """Clean up old notifications."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        statement = select(PushNotifications).where(
            PushNotifications.created_at <= cutoff_date
        )

        notifications = session.exec(statement).all()
        count = 0
        for notification in notifications:
            session.delete(notification)
            count += 1

        session.commit()
        return count


# Create instances
device = CRUDDevice(Device)
push_notifications = CRUDPushNotifications(PushNotifications)

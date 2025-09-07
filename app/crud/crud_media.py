import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlmodel import Session, desc, select

from app.crud.base import CRUDBase
from app.models.media import MediaStore
from app.schemas.media import MediaStoreCreate


class CRUDMediaStores(CRUDBase[MediaStore, MediaStoreCreate, Any]):
    def get_by_object_key(
        self, session: Session, *, object_key: str
    ) -> MediaStore | None:
        """Get media store by object key."""
        statement = select(MediaStore).where(MediaStore.object_key == object_key)
        return session.exec(statement).first()

    def get_by_provider_and_bucket(
        self,
        session: Session,
        *,
        provider: str,
        bucket: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[MediaStore]:
        """Get media stores by provider and bucket."""
        statement = (
            select(MediaStore)
            .where(MediaStore.provider == provider, MediaStore.bucket == bucket)
            .offset(skip)
            .limit(limit)
            .order_by(desc(MediaStore.created_at))
        )
        return list(session.exec(statement).all())

    def get_user_media(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        file_type: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[MediaStore]:
        """Get media files for a user."""
        statement = select(MediaStore).where(
            MediaStore.user_id == user_id, MediaStore.is_deleted == False
        )

        if file_type:
            statement = statement.where(MediaStore.file_type == file_type)

        statement = (
            statement.offset(skip).limit(limit).order_by(desc(MediaStore.created_at))
        )
        return list(session.exec(statement).all())

    def cleanup_old_media(self, session: Session, *, days_old: int = 365) -> int:
        """Clean up old media files."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        statement = select(MediaStore).where(MediaStore.created_at <= cutoff_date)

        media_files = session.exec(statement).all()
        count = 0
        for media_file in media_files:
            session.delete(media_file)
            count += 1

        session.commit()
        return count

    def get_by_storage_class(
        self, session: Session, *, storage_class: str, skip: int = 0, limit: int = 100
    ) -> list[MediaStore]:
        """Get media stores by storage class."""
        statement = (
            select(MediaStore)
            .where(MediaStore.storage_class == storage_class)
            .offset(skip)
            .limit(limit)
            .order_by(desc(MediaStore.created_at))
        )
        return list(session.exec(statement).all())

    def update_url(
        self, session: Session, *, media_id: uuid.UUID, new_url: str
    ) -> MediaStore | None:
        """Update the URL for a media store."""
        media_store = session.get(MediaStore, media_id)
        if media_store:
            media_store.url = new_url
            session.add(media_store)
            session.commit()
            session.refresh(media_store)
            return media_store
        return None

    def get_media_stats(self, session: Session) -> dict:
        """Get statistics about media storage."""
        total_count = len(list(session.exec(select(MediaStore)).all()))

        # Group by provider
        providers = {}
        media_files = session.exec(select(MediaStore)).all()

        for media_file in media_files:
            provider = media_file.provider
            if provider not in providers:
                providers[provider] = 0
            providers[provider] += 1

        return {
            "total_files": total_count,
            "providers": providers,
        }


# Create instance
media_stores = CRUDMediaStores(MediaStore)

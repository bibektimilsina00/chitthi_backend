"""Media service for handling file uploads and storage."""

import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session

from app import crud
from app.models.media import MediaStore
from app.schemas.media import MediaStoreCreate, MediaStoreUpdate


class MediaService:
    """Service for managing media storage and file operations."""

    def upload_media(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        filename: str,
        file_size: int,
        file_type: str,
        storage_path: str,
        original_filename: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MediaStore:
        """Upload and store media file."""
        media_create = MediaStoreCreate(
            user_id=user_id,
            filename=filename,
            original_filename=original_filename or filename,
            file_size=file_size,
            file_type=file_type,
            storage_path=storage_path,
            media_metadata=metadata or {},
        )

        return crud.media_stores.create(session=session, obj_in=media_create)

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
        return crud.media_stores.get_user_media(
            session, user_id=user_id, file_type=file_type, skip=skip, limit=limit
        )

    def get_media_by_id(
        self, session: Session, *, media_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> MediaStore | None:
        """Get media file by ID with optional user verification."""
        media = crud.media_stores.get(session, id=media_id)

        if media and user_id and media.user_id != user_id:
            return None  # User doesn't own this media

        return media

    def delete_media(
        self, session: Session, *, media_id: uuid.UUID, user_id: uuid.UUID
    ) -> MediaStore:
        """Delete a media file."""
        media = crud.media_stores.get(session, id=media_id)

        if not media:
            raise ValueError("Media not found")

        if media.user_id != user_id:
            raise ValueError("You don't have permission to delete this media")

        # Mark as deleted (soft delete)
        media.is_deleted = True
        media.deleted_at = datetime.utcnow()
        session.add(media)
        session.commit()
        session.refresh(media)

        return media

    def update_media_metadata(
        self,
        session: Session,
        *,
        media_id: uuid.UUID,
        user_id: uuid.UUID,
        metadata: dict[str, Any],
    ) -> MediaStore:
        """Update media metadata."""
        media = crud.media_stores.get(session, id=media_id)

        if not media:
            raise ValueError("Media not found")

        if media.user_id != user_id:
            raise ValueError("You don't have permission to update this media")

        media_update = MediaStoreUpdate(media_metadata=metadata)
        return crud.media_stores.update(
            session=session, db_obj=media, obj_in=media_update
        )

    def get_media_statistics(
        self, session: Session, *, user_id: uuid.UUID
    ) -> dict[str, Any]:
        """Get media usage statistics for a user."""
        media_files = crud.media_stores.get_user_media(session, user_id=user_id)

        total_size = sum(m.file_size for m in media_files if not m.is_deleted)
        file_types = {}

        for media in media_files:
            if not media.is_deleted:
                file_types[media.file_type] = file_types.get(media.file_type, 0) + 1

        return {
            "total_files": len([m for m in media_files if not m.is_deleted]),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": file_types,
            "deleted_files": len([m for m in media_files if m.is_deleted]),
        }

    def cleanup_deleted_media(
        self, session: Session, *, days_old: int = 30
    ) -> dict[str, int]:
        """Clean up media files that were deleted more than N days ago."""
        # This would typically involve actual file deletion from storage
        # For now, we'll just return a placeholder
        return {
            "files_cleaned": 0,
            "storage_freed_mb": 0,
        }

    def validate_file_upload(
        self,
        *,
        file_size: int,
        file_type: str,
        user_id: uuid.UUID,
        session: Session,
        max_file_size: int = 50 * 1024 * 1024,  # 50MB default
        allowed_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """Validate if a file upload is allowed."""
        if allowed_types is None:
            allowed_types = [
                "image/jpeg",
                "image/png",
                "image/gif",
                "image/webp",
                "video/mp4",
                "video/webm",
                "video/quicktime",
                "audio/mp3",
                "audio/wav",
                "audio/ogg",
                "audio/m4a",
                "application/pdf",
                "text/plain",
            ]

        validation_result = {
            "valid": True,
            "errors": [],
        }

        # Check file size
        if file_size > max_file_size:
            validation_result["valid"] = False
            validation_result["errors"].append(
                f"File size ({file_size} bytes) exceeds maximum allowed size ({max_file_size} bytes)"
            )

        # Check file type
        if file_type not in allowed_types:
            validation_result["valid"] = False
            validation_result["errors"].append(
                f"File type '{file_type}' is not allowed"
            )

        # Check user storage quota (if implemented)
        user_stats = self.get_media_statistics(session, user_id=user_id)
        max_storage = 1024 * 1024 * 1024  # 1GB per user

        if user_stats["total_size_bytes"] + file_size > max_storage:
            validation_result["valid"] = False
            validation_result["errors"].append("Upload would exceed storage quota")

        return validation_result


media_service = MediaService()

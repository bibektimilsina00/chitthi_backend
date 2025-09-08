"""Authentication service for handling user auth, sessions, and tokens."""

import uuid
from datetime import datetime, timedelta

from sqlmodel import Session

from app import crud
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.auth import RefreshToken, UserSession
from app.models.user import User
from app.schemas.auth import RefreshTokenCreate, UserSessionCreate


class AuthService:
    """Service for handling authentication operations."""

    def authenticate_user(
        self, session: Session, *, username: str, password: str
    ) -> User | None:
        """Authenticate a user by username and password."""
        user = crud.user.get_by_username(session, username=username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def create_user_session(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        device_id: uuid.UUID,
        session_token: str,
        ip: str | None = None,
        user_agent: str | None = None,
        expires_hours: int = 24,
    ) -> UserSession:
        """Create a new user session."""
        expires_at = datetime.utcnow() + timedelta(hours=expires_hours)

        session_create = UserSessionCreate(
            user_id=user_id,
            device_id=device_id,
            session_token=session_token,
            ip=ip,
            user_agent=user_agent,
        )

        user_session = crud.user_session.create(session=session, obj_in=session_create)
        user_session.expires_at = expires_at
        session.add(user_session)
        session.commit()
        session.refresh(user_session)

        return user_session

    def create_refresh_token(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        device_id: uuid.UUID,
        token_hash: str,
        expires_days: int = 30,
    ) -> RefreshToken:
        """Create a new refresh token."""
        expires_at = datetime.utcnow() + timedelta(days=expires_days)

        token_create = RefreshTokenCreate(
            user_id=user_id, device_id=device_id, token_hash=token_hash
        )

        refresh_token = crud.refresh_token.create(session=session, obj_in=token_create)
        refresh_token.expires_at = expires_at
        session.add(refresh_token)
        session.commit()
        session.refresh(refresh_token)

        return refresh_token

    def validate_session(
        self, session: Session, *, session_token: str
    ) -> tuple[UserSession | None, User | None]:
        """Validate a session token and return session and user."""
        user_session = crud.user_session.get_by_token(
            session, session_token=session_token
        )
        if not user_session:
            return None, None

        # Check if session is revoked
        if user_session.revoked:
            return None, None

        # Check if session is expired
        if user_session.expires_at and user_session.expires_at < datetime.utcnow():
            return None, None

        # Get user
        user = crud.user.get(session, id=user_session.user_id)
        if not user or not user.is_active:
            return None, None

        # Update last seen
        crud.user_session.update_last_seen(session, session_id=user_session.id)

        return user_session, user

    def validate_refresh_token(
        self, session: Session, *, token_hash: str
    ) -> tuple[RefreshToken | None, User | None]:
        """Validate a refresh token and return token and user."""
        refresh_token = crud.refresh_token.get_by_token_hash(
            session, token_hash=token_hash
        )
        if not refresh_token:
            return None, None

        # Check if token is expired
        if refresh_token.expires_at and refresh_token.expires_at < datetime.utcnow():
            return None, None

        # Get user
        user = crud.user.get(session, id=refresh_token.user_id)
        if not user or not user.is_active:
            return None, None

        return refresh_token, user

    def refresh_access_token(
        self, session: Session, *, token_hash: str
    ) -> tuple[str | None, UserSession | None]:
        """Create a new access token using a refresh token."""
        refresh_token, user = self.validate_refresh_token(
            session, token_hash=token_hash
        )
        if not refresh_token or not user:
            return None, None

        # Get active session for this device
        sessions = crud.user_session.get_active_sessions(session, user_id=user.id)
        device_session = None
        for s in sessions:
            if s.device_id == refresh_token.device_id:
                device_session = s
                break

        if not device_session:
            return None, None

        # Create new access token
        access_token = create_access_token(
            subject=str(user.id), expires_delta=timedelta(hours=1)
        )

        return access_token, device_session

    def logout_session(self, session: Session, *, session_id: uuid.UUID) -> bool:
        """Logout a specific session."""
        return (
            crud.user_session.revoke_session(session, session_id=session_id) is not None
        )

    def logout_all_sessions(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        except_session_id: uuid.UUID | None = None,
    ) -> int:
        """Logout all sessions for a user except optionally one."""
        sessions_revoked = crud.user_session.revoke_all_user_sessions(
            session, user_id=user_id, except_session_id=except_session_id
        )

        # Also revoke refresh tokens
        tokens_revoked = crud.refresh_token.revoke_user_tokens(session, user_id=user_id)

        return sessions_revoked

    def get_active_sessions(
        self, session: Session, *, user_id: uuid.UUID
    ) -> list[UserSession]:
        """Get all active sessions for a user."""
        return crud.user_session.get_active_sessions(session, user_id=user_id)

    def change_password(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        current_password: str,
        new_password: str,
    ) -> bool:
        """Change user password after verifying current password."""
        user = crud.user.get(session, id=user_id)
        if not user:
            return False

        # Verify current password
        if not verify_password(current_password, user.password_hash):
            return False

        # Update password
        new_password_hash = get_password_hash(new_password)
        crud.user.update(
            session=session, db_obj=user, obj_in={"password_hash": new_password_hash}
        )

        # Revoke all sessions except current one would be handled by caller
        return True

    def cleanup_expired_tokens(self, session: Session) -> dict[str, int]:
        """Clean up expired tokens and sessions."""
        tokens_cleaned = crud.refresh_token.cleanup_expired_tokens(session)

        # Could add session cleanup here too
        return {
            "refresh_tokens_cleaned": tokens_cleaned,
        }


auth_service = AuthService()

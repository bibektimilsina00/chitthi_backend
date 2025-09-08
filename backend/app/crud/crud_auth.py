import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.auth import OAuthProvider, RefreshToken, UserSession
from app.schemas.auth import (
    OAuthProviderCreate,
    RefreshTokenCreate,
    UserSessionCreate,
    UserSessionUpdate,
)


class CRUDUserSession(CRUDBase[UserSession, UserSessionCreate, UserSessionUpdate]):
    def get_active_sessions(
        self, session: Session, *, user_id: uuid.UUID
    ) -> list[UserSession]:
        """Get all active (non-revoked) sessions for a user."""
        statement = select(UserSession).where(
            UserSession.user_id == user_id, UserSession.revoked == False
        )
        return list(session.exec(statement).all())

    def get_by_token(
        self, session: Session, *, session_token: str
    ) -> UserSession | None:
        """Get session by token."""
        statement = select(UserSession).where(
            UserSession.session_token == session_token
        )
        return session.exec(statement).first()

    def revoke_session(
        self, session: Session, *, session_id: uuid.UUID
    ) -> UserSession | None:
        """Revoke a session."""
        user_session = session.get(UserSession, session_id)
        if user_session:
            user_session.revoked = True
            session.add(user_session)
            session.commit()
            session.refresh(user_session)
            return user_session
        return None

    def revoke_all_user_sessions(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        except_session_id: uuid.UUID | None = None,
    ) -> int:
        """Revoke all sessions for a user, optionally except one."""
        statement = select(UserSession).where(
            UserSession.user_id == user_id, UserSession.revoked == False
        )
        if except_session_id:
            statement = statement.where(UserSession.id != except_session_id)

        sessions = session.exec(statement).all()
        count = 0
        for user_session in sessions:
            user_session.revoked = True
            session.add(user_session)
            count += 1

        session.commit()
        return count

    def update_last_seen(
        self, session: Session, *, session_id: uuid.UUID
    ) -> UserSession | None:
        """Update last seen timestamp for a session."""
        user_session = session.get(UserSession, session_id)
        if user_session and not user_session.revoked:
            user_session.last_seen = datetime.utcnow()
            session.add(user_session)
            session.commit()
            session.refresh(user_session)
            return user_session
        return None


class CRUDRefreshToken(CRUDBase[RefreshToken, RefreshTokenCreate, Any]):
    def get_by_token_hash(
        self, session: Session, *, token_hash: str
    ) -> RefreshToken | None:
        """Get refresh token by hash."""
        statement = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash, RefreshToken.revoked_at == None
        )
        return session.exec(statement).first()

    def revoke_token(
        self, session: Session, *, token_id: uuid.UUID
    ) -> RefreshToken | None:
        """Revoke a refresh token."""
        refresh_token = session.get(RefreshToken, token_id)
        if refresh_token:
            refresh_token.revoked_at = datetime.utcnow()
            session.add(refresh_token)
            session.commit()
            session.refresh(refresh_token)
            return refresh_token
        return None

    def revoke_user_tokens(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        except_token_id: uuid.UUID | None = None,
    ) -> int:
        """Revoke all refresh tokens for a user."""
        statement = select(RefreshToken).where(
            RefreshToken.user_id == user_id, RefreshToken.revoked_at == None
        )
        if except_token_id:
            statement = statement.where(RefreshToken.id != except_token_id)

        tokens = session.exec(statement).all()
        count = 0
        for token in tokens:
            token.revoked_at = datetime.utcnow()
            session.add(token)
            count += 1

        session.commit()
        return count

    def cleanup_expired_tokens(self, session: Session) -> int:
        """Remove all expired refresh tokens."""
        now = datetime.utcnow()
        # For now, just clean up revoked tokens since expires_at might be None
        statement = select(RefreshToken).where(RefreshToken.revoked_at != None)

        tokens = session.exec(statement).all()
        count = 0
        for token in tokens:
            # Only delete if revoked more than 30 days ago
            if token.revoked_at and (now - token.revoked_at).days > 30:
                session.delete(token)
                count += 1

        session.commit()
        return count


class CRUDOAuthProvider(CRUDBase[OAuthProvider, OAuthProviderCreate, Any]):
    def get_by_provider_and_user_id(
        self, session: Session, *, provider: str, provider_user_id: str
    ) -> OAuthProvider | None:
        """Get OAuth provider by provider name and external user ID."""
        statement = select(OAuthProvider).where(
            OAuthProvider.provider == provider,
            OAuthProvider.provider_user_id == provider_user_id,
        )
        return session.exec(statement).first()

    def get_user_providers(
        self, session: Session, *, user_id: uuid.UUID
    ) -> list[OAuthProvider]:
        """Get all OAuth providers for a user."""
        statement = select(OAuthProvider).where(OAuthProvider.user_id == user_id)
        return list(session.exec(statement).all())

    def remove_provider(
        self, session: Session, *, user_id: uuid.UUID, provider: str
    ) -> bool:
        """Remove an OAuth provider for a user."""
        statement = select(OAuthProvider).where(
            OAuthProvider.user_id == user_id, OAuthProvider.provider == provider
        )
        oauth_provider = session.exec(statement).first()
        if oauth_provider:
            session.delete(oauth_provider)
            session.commit()
            return True
        return False


# Create instances
user_session = CRUDUserSession(UserSession)
refresh_token = CRUDRefreshToken(RefreshToken)
oauth_provider = CRUDOAuthProvider(OAuthProvider)

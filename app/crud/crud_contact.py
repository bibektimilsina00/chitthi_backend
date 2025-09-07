import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session, desc, select

from app.crud.base import CRUDBase
from app.models.contact import Block, Contact, ContactPermissions
from app.schemas.contact import (
    BlockCreate,
    ContactCreate,
    ContactPermissionCreate,
    ContactUpdate,
)


class CRUDContact(CRUDBase[Contact, ContactCreate, ContactUpdate]):
    def get_user_contacts(
        self, session: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[Contact]:
        """Get all contacts for a user."""
        statement = (
            select(Contact)
            .where(Contact.owner_id == user_id, Contact.is_blocked == False)
            .offset(skip)
            .limit(limit)
            .order_by(desc(Contact.updated_at))
        )
        return list(session.exec(statement).all())

    def get_contact_by_users(
        self, session: Session, *, owner_id: uuid.UUID, contact_user_id: uuid.UUID
    ) -> Contact | None:
        """Get contact relationship between two users."""
        statement = select(Contact).where(
            Contact.owner_id == owner_id, Contact.contact_user_id == contact_user_id
        )
        return session.exec(statement).first()

    def get_user_contact(
        self, session: Session, *, user_id: uuid.UUID, contact_id: uuid.UUID
    ) -> Contact | None:
        """Get a specific contact for a user."""
        statement = select(Contact).where(
            Contact.owner_id == user_id, Contact.id == contact_id
        )
        return session.exec(statement).first()

    def get_favorites(
        self, session: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[Contact]:
        """Get favorite contacts for a user."""
        statement = (
            select(Contact)
            .where(
                Contact.owner_id == user_id,
                Contact.is_favorite == True,
                Contact.is_blocked == False,
            )
            .offset(skip)
            .limit(limit)
            .order_by(desc(Contact.updated_at))
        )
        return list(session.exec(statement).all())

    def toggle_favorite(
        self, session: Session, *, contact_id: uuid.UUID
    ) -> Contact | None:
        """Toggle favorite status of a contact."""
        contact = session.get(Contact, contact_id)
        if contact:
            contact.is_favorite = not contact.is_favorite
            contact.updated_at = datetime.utcnow()
            session.add(contact)
            session.commit()
            session.refresh(contact)
            return contact
        return None

    def update_alias(
        self, session: Session, *, contact_id: uuid.UUID, alias: str | None
    ) -> Contact | None:
        """Update contact alias."""
        contact = session.get(Contact, contact_id)
        if contact:
            contact.alias = alias
            contact.updated_at = datetime.utcnow()
            session.add(contact)
            session.commit()
            session.refresh(contact)
            return contact
        return None

    def block_contact(
        self, session: Session, *, contact_id: uuid.UUID
    ) -> Contact | None:
        """Block a contact."""
        contact = session.get(Contact, contact_id)
        if contact:
            contact.is_blocked = True
            contact.updated_at = datetime.utcnow()
            session.add(contact)
            session.commit()
            session.refresh(contact)
            return contact
        return None

    def unblock_contact(
        self, session: Session, *, contact_id: uuid.UUID
    ) -> Contact | None:
        """Unblock a contact."""
        contact = session.get(Contact, contact_id)
        if contact:
            contact.is_blocked = False
            contact.updated_at = datetime.utcnow()
            session.add(contact)
            session.commit()
            session.refresh(contact)
            return contact
        return None

    def get_blocked_contacts(
        self, session: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[Contact]:
        """Get blocked contacts for a user."""
        statement = (
            select(Contact)
            .where(Contact.owner_id == user_id, Contact.is_blocked == True)
            .offset(skip)
            .limit(limit)
            .order_by(desc(Contact.updated_at))
        )
        return list(session.exec(statement).all())

    def search_contacts(
        self, session: Session, *, user_id: uuid.UUID, query: str, limit: int = 20
    ) -> list[Contact]:
        """Search contacts by alias or username."""
        # This is a simplified search - in production you'd want to join with User table
        statement = (
            select(Contact)
            .where(
                Contact.owner_id == user_id,
                Contact.is_blocked == False,
            )
            .limit(limit)
        )
        return list(session.exec(statement).all())


class CRUDBlock(CRUDBase[Block, BlockCreate, Any]):
    def get_user_blocks(
        self, session: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[Block]:
        """Get all users blocked by a user."""
        statement = (
            select(Block)
            .where(Block.blocker_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(desc(Block.created_at))
        )
        return list(session.exec(statement).all())

    def get_block_relationship(
        self, session: Session, *, blocker_id: uuid.UUID, blocked_id: uuid.UUID
    ) -> Block | None:
        """Check if one user has blocked another."""
        statement = select(Block).where(
            Block.blocker_id == blocker_id, Block.blocked_id == blocked_id
        )
        return session.exec(statement).first()

    def is_blocked(
        self, session: Session, *, blocker_id: uuid.UUID, blocked_id: uuid.UUID
    ) -> bool:
        """Check if one user has blocked another."""
        block = self.get_block_relationship(
            session, blocker_id=blocker_id, blocked_id=blocked_id
        )
        return block is not None

    def unblock_user(
        self, session: Session, *, blocker_id: uuid.UUID, blocked_id: uuid.UUID
    ) -> bool:
        """Unblock a user."""
        block = self.get_block_relationship(
            session, blocker_id=blocker_id, blocked_id=blocked_id
        )
        if block:
            session.delete(block)
            session.commit()
            return True
        return False

    def get_mutual_blocks(
        self, session: Session, *, user1_id: uuid.UUID, user2_id: uuid.UUID
    ) -> tuple[bool, bool]:
        """Check if two users have blocked each other."""
        user1_blocked_user2 = self.is_blocked(
            session, blocker_id=user1_id, blocked_id=user2_id
        )
        user2_blocked_user1 = self.is_blocked(
            session, blocker_id=user2_id, blocked_id=user1_id
        )
        return user1_blocked_user2, user2_blocked_user1

    def get_users_who_blocked(
        self, session: Session, *, blocked_user_id: uuid.UUID, limit: int = 100
    ) -> list[Block]:
        """Get users who have blocked a specific user."""
        statement = (
            select(Block)
            .where(Block.blocked_id == blocked_user_id)
            .limit(limit)
            .order_by(desc(Block.created_at))
        )
        return list(session.exec(statement).all())


class CRUDContactPermissions(
    CRUDBase[ContactPermissions, ContactPermissionCreate, Any]
):
    def get_by_user_and_contact(
        self, session: Session, *, user_id: uuid.UUID, contact_user_id: uuid.UUID
    ) -> ContactPermissions | None:
        """Get contact permissions between two users."""
        statement = select(ContactPermissions).where(
            ContactPermissions.user_id == user_id,
            ContactPermissions.contact_user_id == contact_user_id,
        )
        return session.exec(statement).first()

    def update_permissions(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        contact_user_id: uuid.UUID,
        permission_updates: dict[str, bool],
    ) -> ContactPermissions | None:
        """Update contact permissions."""
        permissions = self.get_by_user_and_contact(
            session, user_id=user_id, contact_user_id=contact_user_id
        )

        if permissions:
            for key, value in permission_updates.items():
                if hasattr(permissions, key):
                    setattr(permissions, key, value)

            permissions.updated_at = datetime.utcnow()
            session.add(permissions)
            session.commit()
            session.refresh(permissions)
            return permissions

        return None


# Create instances
contact = CRUDContact(Contact)
block = CRUDBlock(Block)
contact_permissions = CRUDContactPermissions(ContactPermissions)

"""Contact management service."""

import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session

from app import crud
from app.models.contact import Contact, ContactPermissions
from app.schemas.contact import ContactCreate, ContactPermissionCreate, ContactUpdate


class ContactService:
    """Service for managing user contacts and relationships."""

    def add_contact(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        contact_user_id: uuid.UUID,
        display_name: str | None = None,
        notes: str | None = None,
        is_favorite: bool = False,
    ) -> Contact:
        """Add a new contact."""
        # Check if contact already exists
        existing_contact = crud.contact.get_contact_by_users(
            session, owner_id=user_id, contact_user_id=contact_user_id
        )

        if existing_contact:
            raise ValueError("Contact already exists")

        # Verify the contact user exists
        contact_user = crud.user.get(session, id=contact_user_id)
        if not contact_user:
            raise ValueError("Contact user not found")

        contact_create = ContactCreate(
            contact_user_id=contact_user_id,
            alias=display_name or contact_user.display_name,
            is_favorite=is_favorite,
        )

        return crud.contact.create(session=session, obj_in=contact_create)

    def update_contact(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        contact_id: uuid.UUID,
        updates: dict[str, Any],
    ) -> Contact:
        """Update contact information."""
        contact = crud.contact.get_user_contact(
            session, user_id=user_id, contact_id=contact_id
        )

        if not contact:
            raise ValueError("Contact not found")

        contact_update = ContactUpdate(**updates)
        return crud.contact.update(
            session=session, db_obj=contact, obj_in=contact_update
        )

    def remove_contact(
        self, session: Session, *, user_id: uuid.UUID, contact_id: uuid.UUID
    ) -> Contact:
        """Remove a contact."""
        contact = crud.contact.get_user_contact(
            session, user_id=user_id, contact_id=contact_id
        )

        if not contact:
            raise ValueError("Contact not found")

        return crud.contact.remove(session=session, id=contact_id)

    def get_user_contacts(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        is_favorite: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Contact]:
        """Get user's contacts with optional filtering."""
        return crud.contact.get_user_contacts(
            session,
            user_id=user_id,
            skip=skip,
            limit=limit,
        )

    def get_contact_by_username(
        self, session: Session, *, user_id: uuid.UUID, username: str
    ) -> Contact | None:
        """Find a contact by username."""
        # First find the user by username
        contact_user = crud.user.get_by_username(session, username=username)
        if not contact_user:
            return None

        # Then check if they're in user's contacts
        return crud.contact.get_contact_by_users(
            session, owner_id=user_id, contact_user_id=contact_user.id
        )

    def get_mutual_contacts(
        self, session: Session, *, user_id1: uuid.UUID, user_id2: uuid.UUID
    ) -> list[Contact]:
        """Get mutual contacts between two users."""
        user1_contacts = crud.contact.get_user_contacts(session, user_id=user_id1)
        user2_contacts = crud.contact.get_user_contacts(session, user_id=user_id2)

        # Find contact user IDs that appear in both lists
        user1_contact_ids = {c.contact_user_id for c in user1_contacts}
        user2_contact_ids = {c.contact_user_id for c in user2_contacts}

        mutual_contact_ids = user1_contact_ids & user2_contact_ids

        # Return user1's contact objects for mutual contacts
        return [c for c in user1_contacts if c.contact_user_id in mutual_contact_ids]

    def toggle_favorite(
        self, session: Session, *, user_id: uuid.UUID, contact_id: uuid.UUID
    ) -> Contact:
        """Toggle favorite status for a contact."""
        contact = crud.contact.get_user_contact(
            session, user_id=user_id, contact_id=contact_id
        )

        if not contact:
            raise ValueError("Contact not found")

        contact.is_favorite = not contact.is_favorite
        contact.updated_at = datetime.utcnow()
        session.add(contact)
        session.commit()
        session.refresh(contact)

        return contact

    def set_contact_permissions(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        contact_user_id: uuid.UUID,
        can_see_online_status: bool = True,
        can_see_profile_photo: bool = True,
        can_see_last_seen: bool = True,
        can_add_to_groups: bool = True,
        can_call: bool = True,
    ) -> ContactPermissions:
        """Set permissions for a contact."""
        # Check if contact relationship exists
        contact = crud.contact.get_contact_by_users(
            session, owner_id=user_id, contact_user_id=contact_user_id
        )

        if not contact:
            raise ValueError("Contact relationship not found")

        # Check if permissions already exist
        existing_permissions = crud.contact_permissions.get_by_user_and_contact(
            session, user_id=user_id, contact_user_id=contact_user_id
        )

        if existing_permissions:
            # Update existing permissions
            permission_data = {
                "can_see_online_status": can_see_online_status,
                "can_see_profile_photo": can_see_profile_photo,
                "can_see_last_seen": can_see_last_seen,
                "can_add_to_groups": can_add_to_groups,
                "can_call": can_call,
                "updated_at": datetime.utcnow(),
            }

            for key, value in permission_data.items():
                setattr(existing_permissions, key, value)

            session.add(existing_permissions)
            session.commit()
            session.refresh(existing_permissions)

            return existing_permissions
        else:
            # Create new permissions
            permission_create = ContactPermissionCreate(
                user_id=user_id,
                contact_user_id=contact_user_id,
                can_see_online_status=can_see_online_status,
                can_see_profile_photo=can_see_profile_photo,
                can_see_last_seen=can_see_last_seen,
                can_add_to_groups=can_add_to_groups,
                can_call=can_call,
            )

            return crud.contact_permissions.create(
                session=session, obj_in=permission_create
            )

    def get_contact_permissions(
        self, session: Session, *, user_id: uuid.UUID, contact_user_id: uuid.UUID
    ) -> ContactPermissions | None:
        """Get permissions for a contact."""
        return crud.contact_permissions.get_by_user_and_contact(
            session, user_id=user_id, contact_user_id=contact_user_id
        )

    def can_user_perform_action(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        target_user_id: uuid.UUID,
        action: str,
    ) -> bool:
        """Check if user can perform a specific action with target user."""
        permissions = self.get_contact_permissions(
            session, user_id=target_user_id, contact_user_id=user_id
        )

        if not permissions:
            # Default permissions if none set
            return True

        action_mapping = {
            "see_online_status": permissions.can_see_online_status,
            "see_profile_photo": permissions.can_see_profile_photo,
            "see_last_seen": permissions.can_see_last_seen,
            "add_to_groups": permissions.can_add_to_groups,
            "call": permissions.can_call,
        }

        return action_mapping.get(action, True)

    def block_contact(
        self, session: Session, *, user_id: uuid.UUID, contact_id: uuid.UUID
    ) -> Contact:
        """Block a contact."""
        contact = crud.contact.get_user_contact(
            session, user_id=user_id, contact_id=contact_id
        )

        if not contact:
            raise ValueError("Contact not found")

        contact.is_blocked = True
        contact.blocked_at = datetime.utcnow()
        contact.updated_at = datetime.utcnow()
        session.add(contact)
        session.commit()
        session.refresh(contact)

        return contact

    def unblock_contact(
        self, session: Session, *, user_id: uuid.UUID, contact_id: uuid.UUID
    ) -> Contact:
        """Unblock a contact."""
        contact = crud.contact.get_user_contact(
            session, user_id=user_id, contact_id=contact_id
        )

        if not contact:
            raise ValueError("Contact not found")

        contact.is_blocked = False
        contact.blocked_at = None
        contact.updated_at = datetime.utcnow()
        session.add(contact)
        session.commit()
        session.refresh(contact)

        return contact

    def get_blocked_contacts(
        self, session: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[Contact]:
        """Get user's blocked contacts."""
        return crud.contact.get_blocked_contacts(
            session, user_id=user_id, skip=skip, limit=limit
        )

    def search_contacts(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Contact]:
        """Search user's contacts by display name or notes."""
        return crud.contact.search_contacts(
            session, user_id=user_id, query=query, limit=limit
        )


contact_service = ContactService()

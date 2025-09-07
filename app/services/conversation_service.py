"""Conversation service for managing chat conversations."""

import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session

from app import crud
from app.models.conversation import Conversation, ConversationMember
from app.schemas.conversation import ConversationCreate, ConversationUpdate


class ConversationService:
    """Service for handling conversation operations."""

    def create_conversation(
        self,
        session: Session,
        *,
        conversation_create: ConversationCreate,
        creator_id: uuid.UUID,
        initial_members: list[uuid.UUID] | None = None,
    ) -> Conversation:
        """
        Create a new conversation with initial members.

        Args:
            session: Database session
            conversation_create: Conversation creation data
            creator_id: ID of the conversation creator
            initial_members: List of user IDs to add as initial members
        """
        # Create conversation
        conversation_data = conversation_create.model_dump()
        conversation_data["creator_id"] = creator_id

        conversation = crud.conversation.create(
            session=session, obj_in=ConversationCreate(**conversation_data)
        )

        # Add creator as member
        creator_member = ConversationMember(
            conversation_id=conversation.id, user_id=creator_id, role="admin"
        )
        session.add(creator_member)

        # Add initial members
        if initial_members:
            for user_id in initial_members:
                if user_id != creator_id:  # Don't add creator twice
                    member = ConversationMember(
                        conversation_id=conversation.id, user_id=user_id, role="member"
                    )
                    session.add(member)

        # Update member count
        member_count = 1 + (len(initial_members) if initial_members else 0)
        conversation.member_count = member_count
        session.add(conversation)

        session.commit()
        session.refresh(conversation)
        return conversation

    def get_user_conversations(
        self, session: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[Conversation]:
        """Get all conversations for a user."""
        return crud.conversation.get_user_conversations(
            session, user_id=user_id, skip=skip, limit=limit
        )

    def add_member(
        self,
        session: Session,
        *,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        added_by: uuid.UUID,
        role: str = "member",
    ) -> ConversationMember | None:
        """Add a member to a conversation."""
        # Check if user adding is admin/creator
        adder_member = crud.conversation_member.get_by_conversation_and_user(
            session, conversation_id=conversation_id, user_id=added_by
        )
        if not adder_member or adder_member.role not in ["admin", "creator"]:
            return None

        # Check if user is already a member
        existing_member = crud.conversation_member.get_by_conversation_and_user(
            session, conversation_id=conversation_id, user_id=user_id
        )
        if existing_member:
            return existing_member

        # Add new member
        member = ConversationMember(
            conversation_id=conversation_id, user_id=user_id, role=role
        )
        session.add(member)

        # Update member count
        conversation = crud.conversation.get(session, id=conversation_id)
        if conversation:
            conversation.member_count += 1
            session.add(conversation)

        session.commit()
        session.refresh(member)
        return member

    def remove_member(
        self,
        session: Session,
        *,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        removed_by: uuid.UUID,
    ) -> bool:
        """Remove a member from a conversation."""
        # Check if user removing is admin/creator or removing themselves
        if removed_by != user_id:
            remover_member = crud.conversation_member.get_by_conversation_and_user(
                session, conversation_id=conversation_id, user_id=removed_by
            )
            if not remover_member or remover_member.role not in ["admin", "creator"]:
                return False

        # Get member to remove
        member = crud.conversation_member.get_by_conversation_and_user(
            session, conversation_id=conversation_id, user_id=user_id
        )
        if not member:
            return False

        # Mark as left
        member.left_at = datetime.utcnow()
        session.add(member)

        # Update member count
        conversation = crud.conversation.get(session, id=conversation_id)
        if conversation:
            conversation.member_count = max(0, conversation.member_count - 1)
            session.add(conversation)

        session.commit()
        return True

    def update_member_role(
        self,
        session: Session,
        *,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        new_role: str,
        updated_by: uuid.UUID,
    ) -> ConversationMember | None:
        """Update a member's role in a conversation."""
        # Check if user updating is admin/creator
        updater_member = crud.conversation_member.get_by_conversation_and_user(
            session, conversation_id=conversation_id, user_id=updated_by
        )
        if not updater_member or updater_member.role not in ["admin", "creator"]:
            return None

        # Get member to update
        member = crud.conversation_member.get_by_conversation_and_user(
            session, conversation_id=conversation_id, user_id=user_id
        )
        if not member:
            return None

        # Update role
        member.role = new_role
        session.add(member)
        session.commit()
        session.refresh(member)
        return member

    def mute_conversation(
        self,
        session: Session,
        *,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        is_muted: bool = True,
    ) -> bool:
        """Mute or unmute a conversation for a user."""
        member = crud.conversation_member.get_by_conversation_and_user(
            session, conversation_id=conversation_id, user_id=user_id
        )
        if not member:
            return False

        member.is_muted = is_muted
        session.add(member)
        session.commit()
        return True

    def mark_as_read(
        self,
        session: Session,
        *,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        last_read_message_id: uuid.UUID | None = None,
    ) -> bool:
        """Mark conversation as read up to a specific message."""
        member = crud.conversation_member.get_by_conversation_and_user(
            session, conversation_id=conversation_id, user_id=user_id
        )
        if not member:
            return False

        if last_read_message_id:
            member.last_read_message_id = last_read_message_id
        member.last_read_at = datetime.utcnow()
        member.unread_count = 0

        session.add(member)
        session.commit()
        return True

    def increment_unread_count(
        self,
        session: Session,
        *,
        conversation_id: uuid.UUID,
        exclude_user_id: uuid.UUID | None = None,
    ) -> int:
        """Increment unread count for all members except specified user."""
        members = crud.conversation_member.get_conversation_members(
            session, conversation_id=conversation_id
        )

        count = 0
        for member in members:
            if exclude_user_id and member.user_id == exclude_user_id:
                continue
            member.unread_count += 1
            session.add(member)
            count += 1

        session.commit()
        return count

    def get_conversation_members(
        self, session: Session, *, conversation_id: uuid.UUID, user_id: uuid.UUID
    ) -> list[ConversationMember]:
        """Get conversation members (only if user is a member)."""
        # Verify user is a member
        user_member = crud.conversation_member.get_by_conversation_and_user(
            session, conversation_id=conversation_id, user_id=user_id
        )
        if not user_member:
            return []

        return crud.conversation_member.get_conversation_members(
            session, conversation_id=conversation_id
        )

    def update_conversation(
        self,
        session: Session,
        *,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        conversation_update: ConversationUpdate,
    ) -> Conversation | None:
        """Update conversation details (only by admin/creator)."""
        # Check if user is admin/creator
        member = crud.conversation_member.get_by_conversation_and_user(
            session, conversation_id=conversation_id, user_id=user_id
        )
        if not member or member.role not in ["admin", "creator"]:
            return None

        # Get and update conversation
        conversation = crud.conversation.get(session, id=conversation_id)
        if not conversation:
            return None

        return crud.conversation.update(
            session=session, db_obj=conversation, obj_in=conversation_update
        )

    def archive_conversation(
        self,
        session: Session,
        *,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        archived: bool = True,
    ) -> Conversation | None:
        """Archive or unarchive a conversation."""
        # Check if user is admin/creator
        member = crud.conversation_member.get_by_conversation_and_user(
            session, conversation_id=conversation_id, user_id=user_id
        )
        if not member or member.role not in ["admin", "creator"]:
            return None

        conversation = crud.conversation.get(session, id=conversation_id)
        if not conversation:
            return None

        conversation.archived = archived
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation


conversation_service = ConversationService()

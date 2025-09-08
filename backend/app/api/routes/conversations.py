import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import CurrentUser, SessionDep
from app.schemas.common import Message
from app.schemas.conversation import (
    ConversationCreate,
    ConversationMemberCreate,
    ConversationMemberPublic,
    ConversationMemberUpdate,
    ConversationPublic,
    ConversationsPublic,
    ConversationUpdate,
)
from app.services import conversation_service

router = APIRouter()


@router.get("/", response_model=ConversationsPublic)
def read_conversations(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = Query(default=100, le=100),
) -> Any:
    """
    Retrieve conversations for current user.
    """
    conversations = conversation_service.get_user_conversations(
        session=session, user_id=current_user.id, skip=skip, limit=limit
    )
    # For now, just use length of conversations as count
    count = len(conversations)
    conversations_public = [
        ConversationPublic.model_validate(conv) for conv in conversations
    ]
    return ConversationsPublic(data=conversations_public, count=count)


@router.post("/", response_model=ConversationPublic)
def create_conversation(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    conversation_in: ConversationCreate,
) -> Any:
    """
    Create new conversation.
    """
    conversation = conversation_service.create_conversation(
        session=session, conversation_create=conversation_in, creator_id=current_user.id
    )

    return ConversationPublic.model_validate(conversation)


@router.get("/{id}", response_model=ConversationPublic)
def read_conversation(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Get conversation by ID.
    """
    from app import crud

    conversation = crud.conversation.get(session=session, id=id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Verify user is member of conversation - check via CRUD
    member = crud.conversation_member.get_by_conversation_and_user(
        session, conversation_id=id, user_id=current_user.id
    )
    if not member:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return ConversationPublic.model_validate(conversation)


@router.put("/{id}", response_model=ConversationPublic)
def update_conversation(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    conversation_in: ConversationUpdate,
) -> Any:
    """
    Update a conversation.
    """
    conversation = conversation_service.update_conversation(
        session=session,
        conversation_id=id,
        user_id=current_user.id,
        conversation_update=conversation_in,
    )
    if not conversation:
        raise HTTPException(
            status_code=404, detail="Conversation not found or insufficient permissions"
        )

    return ConversationPublic.model_validate(conversation)


@router.delete("/{id}")
def delete_conversation(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Archive a conversation (we don't really delete, just archive).
    """
    conversation = conversation_service.archive_conversation(
        session=session, conversation_id=id, user_id=current_user.id, archived=True
    )
    if not conversation:
        raise HTTPException(
            status_code=404, detail="Conversation not found or insufficient permissions"
        )

    return Message(message="Conversation archived")


# Conversation Members
@router.get("/{id}/members", response_model=list[ConversationMemberPublic])
def get_members(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get conversation members.
    """
    members = conversation_service.get_conversation_members(
        session=session, conversation_id=id, user_id=current_user.id
    )
    if not members:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return [ConversationMemberPublic.model_validate(member) for member in members]


@router.post("/{id}/members", response_model=ConversationMemberPublic)
def add_member(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    member_in: ConversationMemberCreate,
) -> Any:
    """
    Add member to conversation.
    """
    member = conversation_service.add_member(
        session=session,
        conversation_id=id,
        user_id=member_in.user_id,
        added_by=current_user.id,
        role=getattr(member_in, "role", "member"),
    )
    if not member:
        raise HTTPException(
            status_code=403, detail="Not enough permissions or user already a member"
        )

    return ConversationMemberPublic.model_validate(member)


@router.put("/{id}/members/{member_id}", response_model=ConversationMemberPublic)
def update_member(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    member_id: uuid.UUID,
    member_in: ConversationMemberUpdate,
) -> Any:
    """
    Update conversation member role.
    """
    member = conversation_service.update_member_role(
        session=session,
        conversation_id=id,
        user_id=member_id,
        new_role=member_in.role or "member",
        updated_by=current_user.id,
    )
    if not member:
        raise HTTPException(
            status_code=404, detail="Member not found or insufficient permissions"
        )

    return ConversationMemberPublic.model_validate(member)


@router.delete("/{id}/members/{member_id}")
def remove_member(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID, member_id: uuid.UUID
) -> Message:
    """
    Remove member from conversation.
    """
    success = conversation_service.remove_member(
        session=session,
        conversation_id=id,
        user_id=member_id,
        removed_by=current_user.id,
    )
    if not success:
        raise HTTPException(
            status_code=404, detail="Member not found or insufficient permissions"
        )

    return Message(message="Member removed from conversation")


@router.post("/{id}/leave")
def leave_conversation(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Leave a conversation.
    """
    success = conversation_service.remove_member(
        session=session,
        conversation_id=id,
        user_id=current_user.id,
        removed_by=current_user.id,
    )
    if not success:
        raise HTTPException(status_code=404, detail="Not a member of this conversation")

    return Message(message="Left conversation")


@router.post("/{id}/archive")
def archive_conversation(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Archive a conversation.
    """
    conversation = conversation_service.archive_conversation(
        session=session, conversation_id=id, user_id=current_user.id, archived=True
    )
    if not conversation:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return Message(message="Conversation archived")


@router.post("/{id}/unarchive")
def unarchive_conversation(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Unarchive a conversation.
    """
    conversation = conversation_service.archive_conversation(
        session=session, conversation_id=id, user_id=current_user.id, archived=False
    )
    if not conversation:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return Message(message="Conversation unarchived")


@router.post("/{id}/mute")
def mute_conversation(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Mute notifications for a conversation.
    """
    success = conversation_service.mute_conversation(
        session=session, conversation_id=id, user_id=current_user.id, is_muted=True
    )
    if not success:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return Message(message="Conversation muted")


@router.post("/{id}/unmute")
def unmute_conversation(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Unmute notifications for a conversation.
    """
    success = conversation_service.mute_conversation(
        session=session, conversation_id=id, user_id=current_user.id, is_muted=False
    )
    if not success:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return Message(message="Conversation unmuted")


@router.post("/{id}/read")
def mark_as_read(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Mark conversation as read.
    """
    success = conversation_service.mark_as_read(
        session=session, conversation_id=id, user_id=current_user.id
    )
    if not success:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return Message(message="Conversation marked as read")

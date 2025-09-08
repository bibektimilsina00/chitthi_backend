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
    ConversationWithParticipants,
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
    conversations_data = conversation_service.get_user_conversations(
        session=session, user_id=current_user.id, skip=skip, limit=limit
    )
    # For now, just use length of conversations as count
    count = len(conversations_data)
    conversations_public = [
        ConversationWithParticipants.model_validate(conv) for conv in conversations_data
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


@router.post("/direct/{user_id}", response_model=ConversationWithParticipants)
def create_direct_conversation(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    user_id: uuid.UUID,
) -> Any:
    """
    Create or get existing direct conversation with a specific user.
    """
    from app import crud
    from app.schemas.user import UserPublic
    
    # Check if user exists
    target_user = crud.user.get(session=session, id=user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if direct conversation already exists between these users
    existing_conv = conversation_service.get_direct_conversation(
        session=session, user1_id=current_user.id, user2_id=user_id
    )
    
    if existing_conv:
        # Return existing conversation with participant info
        members = crud.conversation_member.get_conversation_members_with_users(
            session, conversation_id=existing_conv.id
        )
        
        participants = []
        other_participants = []
        
        for member in members:
            if member.user:
                user_public = UserPublic.model_validate(member.user)
                participants.append(user_public)
                if member.user_id != current_user.id:
                    other_participants.append(user_public)
        
        conv_dict = {
            "id": existing_conv.id,
            "type": existing_conv.type,
            "title": existing_conv.title,
            "topic": existing_conv.topic,
            "avatar_url": existing_conv.avatar_url,
            "visibility": existing_conv.visibility,
            "archived": existing_conv.archived,
            "conv_metadata": existing_conv.conv_metadata,
            "creator_id": existing_conv.creator_id,
            "member_count": existing_conv.member_count,
            "last_message_id": existing_conv.last_message_id,
            "created_at": existing_conv.created_at,
            "updated_at": existing_conv.updated_at,
            "participants": participants,
            "other_participants": other_participants,
        }
        return ConversationWithParticipants.model_validate(conv_dict)
    
    # Create new direct conversation
    conversation_create = ConversationCreate(
        type="direct",
        visibility="private",
        creator_id=current_user.id
    )
    
    conversation = conversation_service.create_conversation(
        session=session,
        conversation_create=conversation_create,
        creator_id=current_user.id,
        initial_members=[user_id]
    )
    
    # Load participant info for response
    members = crud.conversation_member.get_conversation_members_with_users(
        session, conversation_id=conversation.id
    )
    
    participants = []
    other_participants = []
    
    for member in members:
        if member.user:
            user_public = UserPublic.model_validate(member.user)
            participants.append(user_public)
            if member.user_id != current_user.id:
                other_participants.append(user_public)
    
    conv_dict = {
        "id": conversation.id,
        "type": conversation.type,
        "title": conversation.title,
        "topic": conversation.topic,
        "avatar_url": conversation.avatar_url,
        "visibility": conversation.visibility,
        "archived": conversation.archived,
        "conv_metadata": conversation.conv_metadata,
        "creator_id": conversation.creator_id,
        "member_count": conversation.member_count,
        "last_message_id": conversation.last_message_id,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "participants": participants,
        "other_participants": other_participants,
    }
    
    return ConversationWithParticipants.model_validate(conv_dict)


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

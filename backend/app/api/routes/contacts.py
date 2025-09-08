import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import CurrentUser, SessionDep
from app.schemas.common import Message
from app.schemas.contact import (
    BlockCreate,
    BlockPublic,
    ContactCreate,
    ContactPublic,
    ContactsPublic,
    ContactUpdate,
)
from app.services import contact_service

router = APIRouter()


@router.get("/", response_model=ContactsPublic)
def read_contacts(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = Query(default=100, le=100),
) -> Any:
    """
    Retrieve contacts for current user.
    """
    contacts = contact_service.get_user_contacts(
        session=session, user_id=current_user.id, skip=skip, limit=limit
    )
    count = len(contacts)
    contacts_public = [ContactPublic.model_validate(contact) for contact in contacts]
    return ContactsPublic(data=contacts_public, count=count)


@router.post("/", response_model=ContactPublic)
def create_contact(
    *, session: SessionDep, current_user: CurrentUser, contact_in: ContactCreate
) -> Any:
    """
    Add a new contact.
    """
    contact = contact_service.add_contact(
        session=session,
        user_id=current_user.id,
        contact_user_id=contact_in.contact_user_id,
        display_name=contact_in.alias,
        is_favorite=getattr(contact_in, "is_favorite", False),
    )
    if not contact:
        raise HTTPException(status_code=400, detail="Unable to add contact")

    return ContactPublic.model_validate(contact)


@router.get("/{id}", response_model=ContactPublic)
def read_contact(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get contact by ID.
    """
    from app import crud

    contact = crud.contact.get_user_contact(
        session=session, user_id=current_user.id, contact_id=id
    )
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    return ContactPublic.model_validate(contact)


@router.put("/{id}", response_model=ContactPublic)
def update_contact(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    contact_in: ContactUpdate,
) -> Any:
    """
    Update a contact.
    """
    contact = contact_service.update_contact(
        session=session,
        user_id=current_user.id,
        contact_id=id,
        updates=contact_in.model_dump(exclude_unset=True),
    )
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    return ContactPublic.model_validate(contact)


@router.delete("/{id}")
def delete_contact(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete a contact.
    """
    success = contact_service.remove_contact(
        session=session, user_id=current_user.id, contact_id=id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Contact not found")

    return Message(message="Contact deleted")


# Block functionality
@router.post("/{id}/block", response_model=BlockPublic)
def block_contact(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    block_in: BlockCreate,
) -> Any:
    """
    Block a contact.
    """
    block = contact_service.block_contact(
        session=session, user_id=current_user.id, contact_id=id
    )
    if not block:
        raise HTTPException(status_code=400, detail="Unable to block contact")

    return BlockPublic.model_validate(block)


@router.delete("/{id}/block")
def unblock_contact(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Unblock a contact.
    """
    success = contact_service.unblock_contact(
        session=session, user_id=current_user.id, contact_id=id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Block not found")

    return Message(message="Contact unblocked")


@router.get("/blocked/", response_model=list[BlockPublic])
def get_blocked_contacts(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = Query(default=100, le=100),
) -> Any:
    """
    Get all blocked contacts.
    """
    blocks = contact_service.get_blocked_contacts(
        session=session, user_id=current_user.id, skip=skip, limit=limit
    )
    return [BlockPublic.model_validate(block) for block in blocks]


@router.post("/search")
def search_contacts(
    session: SessionDep,
    current_user: CurrentUser,
    query: str = Query(..., min_length=1),
) -> Any:
    """
    Search for users to add as contacts.
    """
    from app import crud

    # Simple user search by email pattern (placeholder implementation)
    users = crud.user.get_multi(session=session, skip=0, limit=20)
    # Filter users that match the query pattern
    filtered_users = [
        u
        for u in users
        if u.email and query.lower() in u.email.lower() and u.id != current_user.id
    ]
    # Return simplified user info for search results
    return [
        {"id": u.id, "email": u.email, "display_name": u.display_name}
        for u in filtered_users
    ]

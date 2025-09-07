import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.schemas.contact import BlockBase, ContactBase, ContactPermissionBase

if TYPE_CHECKING:
    from app.models.user import User


class Contact(ContactBase, table=True):
    """Contact database model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id")
    contact_user_id: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    owner: "User" = Relationship(
        back_populates="contacts",
        sa_relationship_kwargs={"foreign_keys": "[Contact.owner_id]"},
    )
    contact_user: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Contact.contact_user_id]"}
    )


class Block(BlockBase, table=True):
    """User blocks database model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    blocker_id: uuid.UUID = Field(foreign_key="user.id")
    blocked_id: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    blocker: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Block.blocker_id]"}
    )
    blocked: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Block.blocked_id]"}
    )


class ContactPermissions(ContactPermissionBase, table=True):
    """Contact permissions database model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    contact_user_id: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ContactPermissions.user_id]"}
    )
    contact_user: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ContactPermissions.contact_user_id]"}
    )

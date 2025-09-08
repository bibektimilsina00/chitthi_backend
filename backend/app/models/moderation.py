import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, SQLModel

from app.schemas.moderation import (
    CallLogBase,
    ModerationLogBase,
    ReportBase,
    ScheduledMessageBase,
    UserBanBase,
)

if TYPE_CHECKING:
    from app.models.conversation import Conversation
    from app.models.user import User


class Reports(ReportBase, table=True):
    """User reports database model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    reporter_id: uuid.UUID = Field(foreign_key="user.id")
    status: str = Field(default="pending")
    reviewed_at: Optional[datetime] = Field(default=None)
    reviewer_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")
    resolution_notes: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ModerationLogs(ModerationLogBase, table=True):
    """Moderation actions log database model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    moderator_id: uuid.UUID = Field(foreign_key="user.id")
    notes: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserBans(UserBanBase, table=True):
    """User bans database model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    banned_by: uuid.UUID = Field(foreign_key="user.id")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ScheduledMessages(ScheduledMessageBase, table=True):
    """Scheduled messages database model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id")
    created_by: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CallLogs(CallLogBase, table=True):
    """Call logs database model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id")
    caller_id: uuid.UUID = Field(foreign_key="user.id")
    callee_id: uuid.UUID = Field(foreign_key="user.id")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Aliases for compatibility with service layer
CallLog = CallLogs
UserReport = Reports
UserBan = UserBans


# Additional models for message reports
class ReportedMessage(SQLModel, table=True):
    """Reported message database model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    reporter_id: uuid.UUID = Field(foreign_key="user.id")
    message_id: uuid.UUID = Field(foreign_key="message.id")
    reason: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    status: str = Field(default="pending", max_length=32)
    reviewed_at: Optional[datetime] = Field(default=None)
    reviewer_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")
    resolution_notes: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

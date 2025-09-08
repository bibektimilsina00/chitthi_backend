import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import JSON
from sqlmodel import Field, SQLModel


class ReportType(str, Enum):
    """Report type enumeration"""

    SPAM = "spam"
    HARASSMENT = "harassment"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    FAKE_ACCOUNT = "fake_account"
    OTHER = "other"


class ModerationAction(str, Enum):
    """Moderation action enumeration"""

    WARNING = "warning"
    TEMPORARY_BAN = "temporary_ban"
    PERMANENT_BAN = "permanent_ban"
    MESSAGE_DELETION = "message_deletion"
    ACCOUNT_SUSPENSION = "account_suspension"


class BanType(str, Enum):
    """Ban type enumeration"""

    TEMPORARY = "temporary"
    PERMANENT = "permanent"


# Report Schemas
class ReportBase(SQLModel):
    """Base schema for user reports"""

    reported_user_id: uuid.UUID
    reason: ReportType
    description: Optional[str] = None
    details: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)


class ReportCreate(ReportBase):
    """Schema for creating a new report"""

    pass


class ReportUpdate(BaseModel):
    """Schema for updating a report"""

    model_config = ConfigDict(extra="forbid")

    status: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    reviewer_id: Optional[uuid.UUID] = None
    resolution_notes: Optional[str] = None


# Moderation Log Schemas
class ModerationLogBase(SQLModel):
    """Base schema for moderation logs"""

    target_user_id: uuid.UUID
    action: ModerationAction
    reason: str
    details: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)


class ModerationLogCreate(ModerationLogBase):
    """Schema for creating a moderation log"""

    moderator_id: uuid.UUID


class ModerationLogUpdate(BaseModel):
    """Schema for updating a moderation log"""

    model_config = ConfigDict(extra="forbid")

    notes: Optional[str] = None


# User Ban Schemas
class UserBanBase(SQLModel):
    """Base schema for user bans"""

    banned_user_id: uuid.UUID
    ban_type: BanType
    reason: str
    expires_at: Optional[datetime] = None


class UserBanCreate(UserBanBase):
    """Schema for creating a user ban"""

    banned_by: uuid.UUID


class UserBanUpdate(BaseModel):
    """Schema for updating a user ban"""

    model_config = ConfigDict(extra="forbid")

    reason: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


# Scheduled Message Schemas
class ScheduledMessageBase(SQLModel):
    """Base schema for scheduled messages"""

    message_payload: dict = Field(sa_type=JSON)
    scheduled_time: datetime
    status: str = Field(default="pending", max_length=32)
    run_at: Optional[datetime] = Field(default=None)


class ScheduledMessageCreate(ScheduledMessageBase):
    """Schema for creating a scheduled message"""

    conversation_id: uuid.UUID
    created_by: uuid.UUID


class ScheduledMessageUpdate(BaseModel):
    """Schema for updating a scheduled message"""

    model_config = ConfigDict(extra="forbid")

    message_payload: Optional[dict] = None
    scheduled_time: Optional[datetime] = None
    status: Optional[str] = None
    run_at: Optional[datetime] = None


# Call Log Schemas
class CallStatus(str, Enum):
    """Call status enumeration"""

    INITIATED = "initiated"
    RINGING = "ringing"
    ANSWERED = "answered"
    ENDED = "ended"
    MISSED = "missed"
    DECLINED = "declined"
    FAILED = "failed"


class CallType(str, Enum):
    """Call type enumeration"""

    VOICE = "voice"
    VIDEO = "video"


class CallLogBase(SQLModel):
    """Base schema for call logs"""

    call_type: str = Field(max_length=16)
    status: str = Field(max_length=32)
    call_metadata: Optional[dict] = Field(default=None, sa_type=JSON)


class CallLogCreate(CallLogBase):
    """Schema for creating a call log"""

    conversation_id: uuid.UUID
    caller_id: uuid.UUID
    callee_id: uuid.UUID


class CallLogUpdate(BaseModel):
    """Schema for updating a call log"""

    model_config = ConfigDict(extra="forbid")

    call_type: Optional[str] = None
    status: Optional[str] = None
    call_metadata: Optional[dict] = None
    ended_at: Optional[datetime] = None
    call_quality_metadata: Optional[Dict[str, Any]] = None


# Message Report Schemas
class ReportedMessageBase(SQLModel):
    """Base schema for reported messages"""

    message_id: uuid.UUID
    reason: str = Field(max_length=255)
    description: Optional[str] = None


class ReportedMessageCreate(ReportedMessageBase):
    """Schema for creating a reported message"""

    reporter_id: uuid.UUID


class ReportedMessageUpdate(BaseModel):
    """Schema for updating a reported message"""

    model_config = ConfigDict(extra="forbid")

    status: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    reviewer_id: Optional[uuid.UUID] = None
    resolution_notes: Optional[str] = None


# Aliases for compatibility
UserReportCreate = ReportCreate
UserReportUpdate = ReportUpdate
UserBanCreate = UserBanCreate  # Already exists
UserBanUpdate = UserBanUpdate  # Already exists
CallLogCreate = CallLogCreate  # Already exists

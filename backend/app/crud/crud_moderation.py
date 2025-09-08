import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session, desc, select

from app.crud.base import CRUDBase
from app.models.moderation import (
    CallLogs,
    ReportedMessage,
    Reports,
    ScheduledMessages,
    UserBans,
)
from app.schemas.moderation import (
    CallLogCreate,
    ReportCreate,
    ReportedMessageCreate,
    ScheduledMessageCreate,
    UserBanCreate,
)


class CRUDReports(CRUDBase[Reports, ReportCreate, Any]):
    def get_pending_reports(
        self, session: Session, *, skip: int = 0, limit: int = 100
    ) -> list[Reports]:
        """Get pending reports."""
        statement = (
            select(Reports)
            .where(Reports.status == "pending")
            .offset(skip)
            .limit(limit)
            .order_by(desc(Reports.created_at))
        )
        return list(session.exec(statement).all())

    def get_user_reports(
        self, session: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[Reports]:
        """Get reports made by a specific user."""
        statement = (
            select(Reports)
            .where(Reports.reporter_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(desc(Reports.created_at))
        )
        return list(session.exec(statement).all())

    def get_reports_against_user(
        self,
        session: Session,
        *,
        reported_user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Reports]:
        """Get reports against a specific user."""
        statement = (
            select(Reports)
            .where(Reports.reported_user_id == reported_user_id)
            .offset(skip)
            .limit(limit)
            .order_by(desc(Reports.created_at))
        )
        return list(session.exec(statement).all())

    def update_status(
        self,
        session: Session,
        *,
        report_id: uuid.UUID,
        status: str,
        assigned_to: uuid.UUID | None = None,
    ) -> Reports | None:
        """Update report status."""
        report = session.get(Reports, report_id)
        if report:
            report.status = status
            if assigned_to:
                report.assigned_to = assigned_to
            report.updated_at = datetime.utcnow()
            session.add(report)
            session.commit()
            session.refresh(report)
            return report
        return None

    def assign_report(
        self, session: Session, *, report_id: uuid.UUID, moderator_id: uuid.UUID
    ) -> Reports | None:
        """Assign a report to a moderator."""
        report = session.get(Reports, report_id)
        if report:
            report.assigned_to = moderator_id
            report.status = "in_review"
            report.updated_at = datetime.utcnow()
            session.add(report)
            session.commit()
            session.refresh(report)
            return report
        return None

    def resolve_report(
        self,
        session: Session,
        *,
        report_id: uuid.UUID,
        moderator_id: uuid.UUID,
        action_taken: str,
        resolution_notes: str | None = None,
    ) -> Reports | None:
        """Resolve a report."""
        report = session.get(Reports, report_id)
        if report:
            report.status = "resolved"
            report.assigned_to = moderator_id
            report.updated_at = datetime.utcnow()
            # You could add more fields to store action_taken and resolution_notes
            session.add(report)
            session.commit()
            session.refresh(report)
            return report
        return None


class CRUDBans(CRUDBase[UserBans, UserBanCreate, Any]):
    def get_active_user_ban(
        self, session: Session, *, user_id: uuid.UUID
    ) -> UserBans | None:
        """Get active ban for a user."""
        statement = select(UserBans).where(
            UserBans.banned_user_id == user_id, UserBans.is_active == True
        )
        return session.exec(statement).first()

    def is_user_banned(self, session: Session, *, user_id: uuid.UUID) -> bool:
        """Check if a user is currently banned."""
        return self.get_active_user_ban(session, user_id=user_id) is not None

    def lift_ban(self, session: Session, *, ban_id: uuid.UUID) -> UserBans | None:
        """Lift a ban by setting it as inactive."""
        ban = session.get(UserBans, ban_id)
        if ban and ban.is_active:
            ban.is_active = False
            session.add(ban)
            session.commit()
            session.refresh(ban)
            return ban
        return None


class CRUDScheduledMessages(CRUDBase[ScheduledMessages, ScheduledMessageCreate, Any]):
    def get_pending_messages(
        self, session: Session, *, limit: int = 100
    ) -> list[ScheduledMessages]:
        """Get messages ready to be sent."""
        now = datetime.utcnow()
        statement = (
            select(ScheduledMessages)
            .where(
                ScheduledMessages.status == "pending",
                ScheduledMessages.scheduled_time <= now,
            )
            .limit(limit)
        )
        return list(session.exec(statement).all())

    def get_user_scheduled_messages(
        self, session: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[ScheduledMessages]:
        """Get scheduled messages for a user."""
        statement = (
            select(ScheduledMessages)
            .where(ScheduledMessages.created_by == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(desc(ScheduledMessages.scheduled_time))
        )
        return list(session.exec(statement).all())

    def mark_as_sent(
        self, session: Session, *, message_id: uuid.UUID
    ) -> ScheduledMessages | None:
        """Mark a scheduled message as sent."""
        scheduled_msg = session.get(ScheduledMessages, message_id)
        if scheduled_msg:
            scheduled_msg.status = "sent"
            scheduled_msg.run_at = datetime.utcnow()
            session.add(scheduled_msg)
            session.commit()
            session.refresh(scheduled_msg)
            return scheduled_msg
        return None

    def mark_as_failed(
        self, session: Session, *, message_id: uuid.UUID, error: str
    ) -> ScheduledMessages | None:
        """Mark a scheduled message as failed."""
        scheduled_msg = session.get(ScheduledMessages, message_id)
        if scheduled_msg:
            scheduled_msg.status = "failed"
            scheduled_msg.run_at = datetime.utcnow()
            # Store error in message_payload if needed
            if scheduled_msg.message_payload is None:
                scheduled_msg.message_payload = {}
            scheduled_msg.message_payload["error"] = error
            session.add(scheduled_msg)
            session.commit()
            session.refresh(scheduled_msg)
            return scheduled_msg
        return None

    def cancel_scheduled_message(
        self, session: Session, *, message_id: uuid.UUID, user_id: uuid.UUID
    ) -> ScheduledMessages | None:
        """Cancel a scheduled message (only by the creator)."""
        scheduled_msg = session.get(ScheduledMessages, message_id)
        if (
            scheduled_msg
            and scheduled_msg.created_by == user_id
            and scheduled_msg.status == "pending"
        ):
            scheduled_msg.status = "cancelled"
            session.add(scheduled_msg)
            session.commit()
            session.refresh(scheduled_msg)
            return scheduled_msg
        return None


class CRUDCallLogs(CRUDBase[CallLogs, CallLogCreate, Any]):
    def get_conversation_calls(
        self,
        session: Session,
        *,
        conversation_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CallLogs]:
        """Get call logs for a conversation."""
        statement = (
            select(CallLogs)
            .where(CallLogs.conversation_id == conversation_id)
            .offset(skip)
            .limit(limit)
            .order_by(desc(CallLogs.started_at))
        )
        return list(session.exec(statement).all())

    def get_user_calls(
        self, session: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[CallLogs]:
        """Get call logs for a user (as caller or callee)."""
        statement = (
            select(CallLogs)
            .where((CallLogs.caller_id == user_id) | (CallLogs.callee_id == user_id))
            .offset(skip)
            .limit(limit)
            .order_by(desc(CallLogs.started_at))
        )
        return list(session.exec(statement).all())

    def end_call(
        self, session: Session, *, call_id: uuid.UUID, status: str = "completed"
    ) -> CallLogs | None:
        """End a call by setting end time and status."""
        call_log = session.get(CallLogs, call_id)
        if call_log and call_log.ended_at is None:
            call_log.ended_at = datetime.utcnow()
            call_log.status = status
            session.add(call_log)
            session.commit()
            session.refresh(call_log)
            return call_log
        return None

    def get_active_calls(
        self, session: Session, *, user_id: uuid.UUID
    ) -> list[CallLogs]:
        """Get active calls for a user."""
        statement = select(CallLogs).where(
            (CallLogs.caller_id == user_id) | (CallLogs.callee_id == user_id),
            CallLogs.ended_at == None,
        )
        return list(session.exec(statement).all())


class CRUDReportedMessage(CRUDBase[ReportedMessage, ReportedMessageCreate, Any]):
    def get_by_reporter_and_message(
        self, session: Session, *, reporter_id: uuid.UUID, message_id: uuid.UUID
    ) -> ReportedMessage | None:
        """Get report by reporter and message."""
        statement = select(ReportedMessage).where(
            ReportedMessage.reporter_id == reporter_id,
            ReportedMessage.message_id == message_id,
        )
        return session.exec(statement).first()

    def get_pending_reports(
        self, session: Session, *, skip: int = 0, limit: int = 100
    ) -> list[ReportedMessage]:
        """Get pending message reports."""
        statement = (
            select(ReportedMessage)
            .where(ReportedMessage.status == "pending")
            .offset(skip)
            .limit(limit)
            .order_by(desc(ReportedMessage.created_at))
        )
        return list(session.exec(statement).all())

    def resolve_report(
        self,
        session: Session,
        *,
        report_id: uuid.UUID,
        moderator_id: uuid.UUID,
        action_taken: str,
        resolution_notes: str | None = None,
    ) -> ReportedMessage | None:
        """Resolve a message report."""
        report = session.get(ReportedMessage, report_id)
        if report:
            report.status = "resolved"
            report.reviewed_at = datetime.utcnow()
            report.reviewer_id = moderator_id
            report.resolution_notes = (
                f"Action: {action_taken}. {resolution_notes or ''}"
            )
            session.add(report)
            session.commit()
            session.refresh(report)
            return report
        return None

    def get_reports_for_user_messages(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        start_date: datetime | None = None,
    ) -> list[ReportedMessage]:
        """Get reports for messages sent by a specific user."""
        # This would need a join with Message table to filter by sender
        # For now, return empty list as placeholder
        return []

    def get_report_statistics(
        self, session: Session, *, start_date: datetime | None = None
    ) -> dict[str, int]:
        """Get report statistics."""
        statement = select(ReportedMessage)
        if start_date:
            statement = statement.where(ReportedMessage.created_at >= start_date)

        reports = list(session.exec(statement).all())

        return {
            "total_reports": len(reports),
            "pending_reports": len([r for r in reports if r.status == "pending"]),
            "resolved_reports": len([r for r in reports if r.status == "resolved"]),
        }


# Create instances
reports = CRUDReports(Reports)
bans = CRUDBans(UserBans)
scheduled_messages = CRUDScheduledMessages(ScheduledMessages)
call_logs = CRUDCallLogs(CallLogs)
reported_message = CRUDReportedMessage(ReportedMessage)

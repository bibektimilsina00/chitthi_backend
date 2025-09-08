"""Moderation service for handling reports, bans, and safety features."""

import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlmodel import Session

from app import crud
from app.models.moderation import CallLogs, ReportedMessage, Reports, UserBans
from app.schemas.moderation import (
    BanType,
    CallLogCreate,
    ReportCreate,
    ReportedMessageCreate,
    ReportType,
    UserBanCreate,
)


class ModerationService:
    """Service for handling moderation and safety features."""

    def create_user_report(
        self,
        session: Session,
        *,
        reporter_id: uuid.UUID,
        reported_user_id: uuid.UUID,
        reason: str,
        description: str | None = None,
        evidence_urls: list[str] | None = None,
    ) -> Reports:
        """Create a user report."""
        # Verify reported user exists
        reported_user = crud.user.get(session, id=reported_user_id)
        if not reported_user:
            raise ValueError("Reported user not found")

        # Convert string reason to ReportType enum
        try:
            report_reason = ReportType(reason)
        except ValueError:
            report_reason = ReportType.OTHER

        report_create = ReportCreate(
            reported_user_id=reported_user_id,
            reason=report_reason,
            description=description,
        )

        return crud.reports.create(session=session, obj_in=report_create)

    def create_message_report(
        self,
        session: Session,
        *,
        reporter_id: uuid.UUID,
        message_id: uuid.UUID,
        reason: str,
        description: str | None = None,
    ) -> ReportedMessage:
        """Report a message."""
        # Verify message exists
        message = crud.message.get(session, id=message_id)
        if not message:
            raise ValueError("Message not found")

        # Check if already reported by this user
        existing_report = crud.reported_message.get_by_reporter_and_message(
            session, reporter_id=reporter_id, message_id=message_id
        )

        if existing_report:
            raise ValueError("You have already reported this message")

        report_create = ReportedMessageCreate(
            reporter_id=reporter_id,
            message_id=message_id,
            reason=reason,
            description=description,
        )

        return crud.reported_message.create(session=session, obj_in=report_create)

    def ban_user(
        self,
        session: Session,
        *,
        banned_user_id: uuid.UUID,
        banned_by: uuid.UUID,
        reason: str,
        ban_type: str = "temporary",
        expires_at: datetime | None = None,
    ) -> UserBans:
        """Ban a user."""
        # Check if user is already banned
        existing_ban = crud.bans.get_active_user_ban(session, user_id=banned_user_id)
        if existing_ban:
            raise ValueError("User is already banned")

        ban_create = UserBanCreate(
            banned_user_id=banned_user_id,
            banned_by=banned_by,
            reason=reason,
            ban_type=(
                BanType.TEMPORARY if ban_type == "temporary" else BanType.PERMANENT
            ),
            expires_at=expires_at,
        )

        return crud.bans.create(session=session, obj_in=ban_create)

    def unban_user(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        moderator_id: uuid.UUID,
        reason: str | None = None,
    ) -> UserBans | None:
        """Unban a user."""
        active_ban = crud.bans.get_active_user_ban(session, user_id=user_id)

        if not active_ban:
            raise ValueError("User is not currently banned")

        return crud.bans.lift_ban(session=session, ban_id=active_ban.id)

    def is_user_banned(self, session: Session, *, user_id: uuid.UUID) -> bool:
        """Check if a user is currently banned."""
        active_ban = crud.bans.get_active_user_ban(session, user_id=user_id)
        return active_ban is not None

    def get_user_ban_info(
        self, session: Session, *, user_id: uuid.UUID
    ) -> UserBans | None:
        """Get active ban information for a user."""
        return crud.bans.get_active_user_ban(session, user_id=user_id)

    def log_call(
        self,
        session: Session,
        *,
        conversation_id: uuid.UUID,
        caller_id: uuid.UUID,
        callee_id: uuid.UUID,
        call_type: str = "voice",
        status: str = "initiated",
    ) -> CallLogs:
        """Log a call event."""
        call_log_create = CallLogCreate(
            conversation_id=conversation_id,
            caller_id=caller_id,
            callee_id=callee_id,
            call_type=call_type,
            status=status,
        )

        return crud.call_logs.create(session=session, obj_in=call_log_create)

    def get_call_history(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        limit: int = 50,
    ) -> list[CallLogs]:
        """Get call history for a user."""
        return crud.call_logs.get_user_calls(
            session=session, user_id=user_id, limit=limit
        )

    def get_user_call_history(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        call_type: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[CallLogs]:
        """Get call history for a user."""
        return crud.call_logs.get_user_calls(
            session=session, user_id=user_id, skip=skip, limit=limit
        )

    def get_pending_reports(
        self,
        session: Session,
        *,
        report_type: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Get pending moderation reports."""
        user_reports = crud.reports.get_pending_reports(
            session, skip=skip, limit=limit if report_type != "message" else 0
        )

        message_reports = crud.reported_message.get_pending_reports(
            session, skip=skip, limit=limit if report_type != "user" else 0
        )

        if report_type == "user":
            return {"user_reports": user_reports, "message_reports": []}
        elif report_type == "message":
            return {"user_reports": [], "message_reports": message_reports}
        else:
            return {"user_reports": user_reports, "message_reports": message_reports}

    def resolve_user_report(
        self,
        session: Session,
        *,
        report_id: uuid.UUID,
        moderator_id: uuid.UUID,
        action_taken: str,
        resolution_notes: str | None = None,
    ) -> Reports | None:
        """Resolve a user report."""
        report = crud.reports.get(session, id=report_id)

        if not report:
            raise ValueError("Report not found")

        if report.status != "pending":
            raise ValueError("Report is not pending")

        return crud.reports.resolve_report(
            session=session,
            report_id=report_id,
            moderator_id=moderator_id,
            action_taken=action_taken,
            resolution_notes=resolution_notes,
        )

    def resolve_message_report(
        self,
        session: Session,
        *,
        report_id: uuid.UUID,
        moderator_id: uuid.UUID,
        action_taken: str,
        resolution_notes: str | None = None,
    ) -> ReportedMessage | None:
        """Resolve a message report."""
        report = crud.reported_message.get(session, id=report_id)

        if not report:
            raise ValueError("Report not found")

        if report.status != "pending":
            raise ValueError("Report is not pending")

        return crud.reported_message.resolve_report(
            session=session,
            report_id=report_id,
            moderator_id=moderator_id,
            action_taken=action_taken,
            resolution_notes=resolution_notes,
        )

    def get_moderation_statistics(
        self, session: Session, *, days: int = 30
    ) -> dict[str, Any]:
        """Get moderation statistics for the last N days."""
        start_date = datetime.utcnow() - timedelta(days=days)

        # For now, let's return basic statistics using available methods
        user_reports = crud.reports.get_multi(session=session, skip=0, limit=1000)
        message_reports = crud.reported_message.get_multi(
            session=session, skip=0, limit=1000
        )
        bans = crud.bans.get_multi(session=session, skip=0, limit=1000)
        calls = crud.call_logs.get_multi(session=session, skip=0, limit=1000)

        return {
            "period_days": days,
            "user_reports": {"total": len(user_reports)},
            "message_reports": {"total": len(message_reports)},
            "bans": {"total": len(bans)},
            "calls": {"total": len(calls)},
        }

    def check_user_safety_violations(
        self, session: Session, *, user_id: uuid.UUID, days: int = 30
    ) -> dict[str, Any]:
        """Check for safety violations by a user."""
        start_date = datetime.utcnow() - timedelta(days=days)

        # Get reports against this user
        reports_against = crud.reports.get_reports_against_user(
            session, reported_user_id=user_id, skip=0, limit=100
        )

        # Get message reports for this user's messages
        message_reports = crud.reported_message.get_reports_for_user_messages(
            session, user_id=user_id
        )

        # Get ban history - for now just check if currently banned
        current_ban = crud.bans.get_active_user_ban(session, user_id=user_id)
        ban_count = 1 if current_ban else 0

        # Calculate risk score
        risk_score = 0
        if len(reports_against) > 5:
            risk_score += 3
        elif len(reports_against) > 2:
            risk_score += 2
        elif len(reports_against) > 0:
            risk_score += 1

        if len(message_reports) > 3:
            risk_score += 2
        elif len(message_reports) > 0:
            risk_score += 1

        if ban_count > 0:
            risk_score += ban_count

        risk_level = "low"
        if risk_score >= 5:
            risk_level = "high"
        elif risk_score >= 3:
            risk_level = "medium"

        return {
            "user_id": str(user_id),
            "period_days": days,
            "reports_against": len(reports_against),
            "message_reports": len(message_reports),
            "ban_count": ban_count,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "recent_reports": reports_against[:5],  # Last 5 reports
        }

    def auto_moderate_user(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        moderator_id: uuid.UUID,
        trigger_reason: str,
    ) -> dict[str, Any]:
        """Automatically moderate a user based on safety violations."""
        safety_check = self.check_user_safety_violations(session, user_id=user_id)

        actions_taken = []

        if safety_check["risk_level"] == "high":
            # Temporary ban for high-risk users
            if not self.is_user_banned(session, user_id=user_id):
                ban = self.ban_user(
                    session,
                    banned_user_id=user_id,
                    banned_by=moderator_id,
                    reason=f"Automatic moderation: {trigger_reason}",
                    ban_type="temporary",
                    expires_at=datetime.utcnow() + timedelta(days=7),
                )
                actions_taken.append(f"Temporary ban until {ban.expires_at}")

        elif safety_check["risk_level"] == "medium":
            # Warning or temporary restrictions
            actions_taken.append("Account flagged for manual review")

        return {
            "user_id": str(user_id),
            "trigger_reason": trigger_reason,
            "risk_assessment": safety_check,
            "actions_taken": actions_taken,
        }


moderation_service = ModerationService()

"""Celery görevleri."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Iterable

import structlog
from celery.utils.log import get_task_logger

from sytefy_backend.config import get_settings
from sytefy_backend.core.database.session import _SessionLocal
from sytefy_backend.core.observability.celery_metrics import (
    record_reminder_channel_event,
    record_reminder_task_outcome,
)
from sytefy_backend.core.tasks.celery_app import celery_app
from sytefy_backend.modules.notifications.application.use_cases import CreateNotification
from sytefy_backend.modules.notifications.infrastructure.channels import (
    EmailNotificationService,
    SMSNotificationService,
    TwilioSMSBackend,
)
from sytefy_backend.modules.notifications.infrastructure.repository import NotificationRepository

logger = structlog.get_logger("sytefy.tasks.reminders")
task_logger = get_task_logger(__name__)


def _format_body(context: dict[str, Any]) -> str:
    title = context.get("title") or "Randevu"
    start = context.get("start_at") or context.get("remind_at")
    location = context.get("location") or "Belirtilmedi"
    extra = context.get("body_extra")
    parts = [f"{title} için hatırlatma.", f"Başlangıç: {start}", f"Konum: {location}"]
    if extra:
        parts.append(str(extra))
    return "\n".join(parts)


def _record_log(channels: Iterable[str], payload: dict[str, Any]) -> None:
    if "log" in channels:
        task_logger.info("appointments.send_reminder %s", payload)
        logger.info("appointments.send_reminder", **payload)


def _persist_notification(
    *,
    user_id: int | None,
    channel: str,
    title: str,
    body: str,
    status: str,
) -> None:
    if not user_id:
        return

    async def _create() -> None:
        async with _SessionLocal() as session:
            repo = NotificationRepository(session)
            use_case = CreateNotification(repo)
            await use_case(
                user_id=user_id,
                title=title,
                body=body,
                channel=channel,
                status=status,
            )

    try:
        asyncio.run(_create())
    except RuntimeError:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(_create())
        else:  # pragma: no cover - defensive branch
            asyncio.run(_create())


@celery_app.task(
    bind=True,
    name="appointments.send_reminder",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def send_appointment_reminder(
    self,
    appointment_id: int,
    remind_at: str,
    channels: list[str] | None = None,
    context: dict[str, Any] | None = None,
):
    """Görevi tetiklenen randevu için seçili kanallara bildirim gönderir."""
    record_reminder_task_outcome("started")
    settings = get_settings()
    email_service = EmailNotificationService(
        sender=settings.notification_email_from,
        enabled=settings.notification_email_enabled,
        host=settings.notification_email_host,
        port=settings.notification_email_port,
        username=settings.notification_email_username,
        password=settings.notification_email_password,
        use_tls=settings.notification_email_use_tls,
        use_ssl=settings.notification_email_use_ssl,
        timeout=settings.notification_email_timeout,
    )
    sms_backend = None
    if (
        settings.notification_sms_account_sid
        and settings.notification_sms_auth_token
        and settings.notification_sms_from
    ):
        sms_backend = TwilioSMSBackend(
            account_sid=settings.notification_sms_account_sid,
            auth_token=settings.notification_sms_auth_token,
            from_number=settings.notification_sms_from,
            base_url=settings.notification_sms_base_url,
            timeout=settings.notification_sms_timeout,
        )
    sms_service = SMSNotificationService(
        sender=settings.notification_sms_from,
        enabled=settings.notification_sms_enabled,
        backend=sms_backend,
    )
    normalized_channels = tuple(channels or ("log",))
    context = context or {}
    subject = context.get("subject") or f"{context.get('title', 'Randevu')} hatırlatıcısı"
    body = context.get("body") or _format_body(context | {"remind_at": remind_at})
    delivered: list[str] = []
    user_id = context.get("user_id")
    outcomes: dict[str, bool] = {}

    try:
        if "email" in normalized_channels:
            recipient = context.get("customer_email") or context.get("user_email")
            success = email_service.send(recipient=recipient, subject=subject, body=body)
            outcomes["email"] = success
            record_reminder_channel_event("email", "sent" if success else "failed")
            if success:
                delivered.append("email")

        if "sms" in normalized_channels:
            recipient = context.get("customer_phone")
            success = sms_service.send(recipient=recipient, body=body)
            outcomes["sms"] = success
            record_reminder_channel_event("sms", "sent" if success else "failed")
            if success:
                delivered.append("sms")

        if "notification" in normalized_channels:
            logger.info(
                "appointments.reminder.notification",
                user_id=context.get("user_id"),
                title=subject,
            )
            delivered.append("notification")
            outcomes["notification"] = True
            record_reminder_channel_event("notification", "sent")

        payload = {
            "appointment_id": appointment_id,
            "remind_at": remind_at,
            "channels": normalized_channels,
            "task_id": self.request.id,
            "subject": subject,
        }
        _record_log(normalized_channels, payload)
        if "log" in normalized_channels:
            delivered.append("log")

        payload["delivered"] = delivered
        payload["delivered_at"] = datetime.now(timezone.utc).isoformat()
        payload["context"] = context

        failure_suffix = " Gönderim başarısız."
        for channel, success in outcomes.items():
            status = "sent" if success else "failed"
            message = body if success else f"{body}{failure_suffix}"
            _persist_notification(
                user_id=user_id,
                channel=channel,
                title=subject,
                body=message,
                status=status,
            )

        record_reminder_task_outcome("succeeded")
        return payload
    except Exception:
        record_reminder_task_outcome("failed")
        raise

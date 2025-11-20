"""Celery-backed notification dispatcher."""

from __future__ import annotations

from sytefy_backend.modules.notifications.application.use_cases import NotificationDispatcher
from sytefy_backend.modules.notifications.domain.entities import Notification
from sytefy_backend.modules.notifications.tasks import deliver_notification


class CeleryNotificationDispatcher(NotificationDispatcher):
    def dispatch(self, notification: Notification) -> None:
        deliver_notification.delay(
            notification_id=notification.id or 0,
            user_id=notification.user_id,
            channel=notification.channel,
            title=notification.title,
        )

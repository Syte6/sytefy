"""Celery task for notifications."""

from __future__ import annotations

import structlog
from celery.utils.log import get_task_logger

from sytefy_backend.core.tasks.celery_app import celery_app

logger = structlog.get_logger("sytefy.notifications")
task_logger = get_task_logger(__name__)


@celery_app.task(
    bind=True,
    name="notifications.deliver",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def deliver_notification(self, *, notification_id: int, user_id: int, channel: str, title: str):
    payload = {
        "notification_id": notification_id,
        "user_id": user_id,
        "channel": channel,
        "title": title,
        "task_id": self.request.id,
    }
    task_logger.info("notifications.deliver %s", payload)
    logger.info("notifications.deliver", **payload)
    return payload

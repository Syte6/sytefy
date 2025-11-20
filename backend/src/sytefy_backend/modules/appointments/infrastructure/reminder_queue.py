"""Celery tabanlı hatırlatıcı kuyruğu."""

from __future__ import annotations

from datetime import timezone

from celery import Celery

from sytefy_backend.modules.appointments.application.reminders import ReminderTaskClient
from sytefy_backend.modules.appointments.domain.entities import AppointmentReminder
from sytefy_backend.modules.appointments.tasks import send_appointment_reminder


class CeleryReminderTaskClient(ReminderTaskClient):
    def __init__(self, app: Celery):
        self._app = app

    def enqueue(self, *, reminder: AppointmentReminder) -> str:
        remind_at = reminder.remind_at.astimezone(timezone.utc)
        result = send_appointment_reminder.apply_async(
            args=[reminder.appointment_id],
            kwargs={
                "channels": list(reminder.channels),
                "remind_at": remind_at.isoformat(),
                "context": reminder.payload or {},
            },
            eta=remind_at,
        )
        return result.id

    def revoke(self, task_id: str) -> None:
        if task_id:
            self._app.control.revoke(task_id, terminate=False)


__all__ = ["CeleryReminderTaskClient"]

"""Use cases for scheduling appointment reminders."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping, Protocol, Sequence

from sytefy_backend.modules.appointments.domain.entities import AppointmentReminder


class ReminderTaskClient(Protocol):
    def enqueue(self, *, reminder: AppointmentReminder) -> str: ...

    def revoke(self, task_id: str) -> None: ...


@dataclass(slots=True)
class ReminderScheduled:
    appointment_id: int
    remind_at: datetime
    task_id: str


class ScheduleAppointmentReminder:
    def __init__(self, task_client: ReminderTaskClient, offset_minutes: int):
        self._task_client = task_client
        self._offset = offset_minutes

    def __call__(
        self,
        *,
        appointment_id: int,
        appointment_time: datetime,
        channels: Sequence[str] | None = None,
        payload: Mapping[str, Any] | None = None,
    ) -> ReminderScheduled:
        if appointment_time.tzinfo is None:
            appointment_time = appointment_time.replace(tzinfo=timezone.utc)
        else:
            appointment_time = appointment_time.astimezone(timezone.utc)
        remind_at = appointment_time - timedelta(minutes=self._offset)
        if remind_at.tzinfo is None:
            remind_at = remind_at.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        remind_ts = remind_at.timestamp()
        now_ts = now.timestamp()
        if remind_ts < now_ts:
            remind_at = now
        reminder = AppointmentReminder(
            appointment_id=appointment_id,
            remind_at=remind_at,
            channels=tuple(channels or ("log",)),
            payload=dict(payload or {}),
        )
        task_id = self._task_client.enqueue(reminder=reminder)
        return ReminderScheduled(appointment_id=appointment_id, remind_at=remind_at, task_id=task_id)

    def cancel(self, task_id: str | None) -> None:
        if task_id:
            self._task_client.revoke(task_id)

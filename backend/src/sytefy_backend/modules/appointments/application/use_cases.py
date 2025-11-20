"""Application layer use cases for appointments."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Sequence

from sytefy_backend.core.exceptions import ApplicationError
from sytefy_backend.modules.appointments.application.interfaces import IAppointmentRepository
from sytefy_backend.modules.appointments.domain.entities import Appointment
from sytefy_backend.modules.appointments.application.reminders import ReminderScheduled, ScheduleAppointmentReminder
from sytefy_backend.modules.customers.application.interfaces import ICustomerRepository


@dataclass(slots=True)
class CreateAppointmentResult:
    appointment: Appointment
    reminder: ReminderScheduled | None


async def _build_reminder_payload(
    appointment: Appointment,
    *,
    user_email: str | None,
    customer_repo: ICustomerRepository | None,
) -> dict[str, Any]:
    customer_name: str | None = None
    customer_email: str | None = None
    customer_phone: str | None = None
    if customer_repo and appointment.customer_id:
        customer = await customer_repo.get_by_id(appointment.customer_id)
        if customer:
            customer_name = customer.name
            customer_email = customer.email
            customer_phone = customer.phone
    start_iso = appointment.start_at.astimezone(timezone.utc).isoformat()
    end_iso = appointment.end_at.astimezone(timezone.utc).isoformat()
    location = appointment.location or ""
    body = (
        f"{appointment.title} randevusu {start_iso} tarihinde başlayacak."
        f" {('Konum: ' + location) if location else ''}"
    ).strip()
    return {
        "user_id": appointment.user_id,
        "user_email": user_email,
        "customer_id": appointment.customer_id,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "customer_phone": customer_phone,
        "title": appointment.title,
        "location": location,
        "start_at": start_iso,
        "end_at": end_iso,
        "body": body,
    }


class CreateAppointment:
    def __init__(
        self,
        repo: IAppointmentRepository,
        reminder_scheduler: ScheduleAppointmentReminder,
        default_channels: Sequence[str] | None = None,
        customer_repo: ICustomerRepository | None = None,
    ):
        self._repo = repo
        self._scheduler = reminder_scheduler
        self._default_channels = tuple(default_channels or ("log",))
        self._customer_repo = customer_repo

    async def __call__(
        self,
        *,
        user_id: int,
        user_email: str | None,
        customer_id: int | None,
        title: str,
        description: str | None,
        location: str | None,
        channel: str,
        start_at: datetime,
        end_at: datetime,
        reminder_channels: Sequence[str] | None = None,
    ) -> CreateAppointmentResult:
        if end_at <= start_at:
            raise ApplicationError("Bitiş zamanı başlangıçtan büyük olmalı.")
        if start_at.tzinfo is None:
            start_at = start_at.replace(tzinfo=timezone.utc)
        else:
            start_at = start_at.astimezone(timezone.utc)
        if end_at.tzinfo is None:
            end_at = end_at.replace(tzinfo=timezone.utc)
        else:
            end_at = end_at.astimezone(timezone.utc)
        channels = tuple(reminder_channels or self._default_channels)
        appointment = Appointment(
            id=None,
            user_id=user_id,
            customer_id=customer_id,
            title=title,
            description=description,
            location=location,
            channel=channel,
            start_at=start_at,
            end_at=end_at,
            remind_at=None,
            reminder_channels=channels,
            reminder_task_id=None,
        )
        stored = await self._repo.create(appointment)
        reminder: ReminderScheduled | None = None
        if channels:
            payload = await _build_reminder_payload(
                stored,
                user_email=user_email,
                customer_repo=self._customer_repo,
            )
            reminder = self._scheduler(
                appointment_id=stored.id or 0,
                appointment_time=appointment.start_at,
                channels=channels,
                payload=payload,
            )
            stored = await self._repo.update_reminder_metadata(
                appointment_id=stored.id or 0,
                remind_at=reminder.remind_at,
                reminder_task_id=reminder.task_id,
                channels=channels,
            )
        return CreateAppointmentResult(appointment=stored, reminder=reminder)


class ListAppointments:
    def __init__(self, repo: IAppointmentRepository):
        self._repo = repo

    async def __call__(
        self,
        *,
        user_id: int,
        status: str | None = None,
        start_from: datetime | None = None,
        start_to: datetime | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> tuple[int, list[Appointment]]:
        return await self._repo.list_by_user(
            user_id=user_id,
            status=status,
            start_from=start_from,
            start_to=start_to,
            limit=limit,
            offset=offset,
        )


class AppointmentNotFound(ApplicationError):
    def __init__(self):
        super().__init__("Randevu bulunamadı.")


ALLOWED_STATUSES = {"scheduled", "confirmed", "completed", "cancelled", "no_show"}
FINAL_STATUSES = {"completed", "cancelled", "no_show"}
STATUS_TRANSITIONS = {
    "scheduled": {"scheduled", "confirmed", "completed", "cancelled", "no_show"},
    "confirmed": {"confirmed", "completed", "cancelled", "no_show"},
    "completed": {"completed"},
    "cancelled": {"cancelled"},
    "no_show": {"no_show"},
}


def _validate_status_transition(current: str, new: str) -> None:
    new = new.lower()
    if new not in ALLOWED_STATUSES:
        raise ApplicationError("Geçersiz statü değeri.")
    if new not in STATUS_TRANSITIONS.get(current, {current}):
        raise ApplicationError("Mevcut statüden bu statüye geçiş yapılamaz.")


class UpdateAppointment:
    def __init__(
        self,
        repo: IAppointmentRepository,
        reminder_scheduler: ScheduleAppointmentReminder,
        customer_repo: ICustomerRepository | None = None,
    ):
        self._repo = repo
        self._scheduler = reminder_scheduler
        self._customer_repo = customer_repo

    async def __call__(
        self,
        *,
        appointment_id: int,
        user_id: int,
        user_email: str | None,
        title: str | None = None,
        description: str | None = None,
        location: str | None = None,
        channel: str | None = None,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
        reminder_channels: Sequence[str] | None = None,
        status: str | None = None,
    ) -> Appointment:
        existing = await self._repo.get_by_id(appointment_id)
        if not existing or existing.user_id != user_id:
            raise AppointmentNotFound()
        original_status = existing.status
        start_changed = False
        channels_changed = False
        status_changed = False
        if start_at:
            if start_at.tzinfo is None:
                start_at = start_at.replace(tzinfo=timezone.utc)
            else:
                start_at = start_at.astimezone(timezone.utc)
            existing.start_at = start_at
            start_changed = True
        if end_at:
            if end_at.tzinfo is None:
                end_at = end_at.replace(tzinfo=timezone.utc)
            else:
                end_at = end_at.astimezone(timezone.utc)
            existing.end_at = end_at
        if existing.end_at <= existing.start_at:
            raise ApplicationError("Bitiş zamanı başlangıçtan büyük olmalı.")
        if title is not None:
            existing.title = title
        if description is not None:
            existing.description = description
        if location is not None:
            existing.location = location
        if channel is not None:
            existing.channel = channel
        if status is not None:
            status = status.lower()
            _validate_status_transition(existing.status, status)
            existing.status = status
            status_changed = status != original_status
        if reminder_channels is not None:
            existing.reminder_channels = tuple(reminder_channels)
            channels_changed = True

        should_cancel_reminder = existing.status in FINAL_STATUSES
        if should_cancel_reminder and existing.reminder_task_id:
            self._scheduler.cancel(existing.reminder_task_id)
            existing.reminder_task_id = None
            existing.remind_at = None
            existing.reminder_channels = tuple()

        updated = await self._repo.update(existing)

        should_reschedule = (
            not should_cancel_reminder
            and bool(existing.reminder_channels)
            and (start_changed or channels_changed or status_changed)
        )
        if should_reschedule:
            payload = await _build_reminder_payload(
                updated,
                user_email=user_email,
                customer_repo=self._customer_repo,
            )
            reminder = self._scheduler(
                appointment_id=updated.id or 0,
                appointment_time=updated.start_at,
                channels=existing.reminder_channels,
                payload=payload,
            )
            updated = await self._repo.update_reminder_metadata(
                appointment_id=updated.id or 0,
                remind_at=reminder.remind_at,
                reminder_task_id=reminder.task_id,
                channels=existing.reminder_channels,
            )
        return updated


class CancelAppointment:
    def __init__(self, repo: IAppointmentRepository, reminder_scheduler: ScheduleAppointmentReminder):
        self._repo = repo
        self._scheduler = reminder_scheduler

    async def __call__(self, *, appointment_id: int, user_id: int) -> Appointment:
        existing = await self._repo.get_by_id(appointment_id)
        if not existing or existing.user_id != user_id:
            raise AppointmentNotFound()
        if existing.status in {"completed", "cancelled"}:
            raise ApplicationError("Bu randevu zaten sonuçlandırılmış.")
        if existing.reminder_task_id:
            self._scheduler.cancel(existing.reminder_task_id)
        existing.status = "cancelled"
        existing.reminder_channels = tuple()
        existing.reminder_task_id = None
        existing.remind_at = None
        return await self._repo.update(existing)

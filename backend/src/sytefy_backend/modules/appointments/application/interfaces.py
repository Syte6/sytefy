"""Repository interfaces for appointments."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from sytefy_backend.modules.appointments.domain.entities import Appointment


class IAppointmentRepository(Protocol):
    async def create(self, appointment: Appointment) -> Appointment: ...

    async def list_by_user(
        self,
        *,
        user_id: int,
        status: str | None = None,
        start_from: datetime | None = None,
        start_to: datetime | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> tuple[int, list[Appointment]]: ...

    async def update_reminder_metadata(
        self,
        *,
        appointment_id: int,
        remind_at: datetime | None,
        reminder_task_id: str | None,
        channels: tuple[str, ...],
    ) -> Appointment: ...

    async def update(self, appointment: Appointment) -> Appointment: ...

    async def get_by_id(self, appointment_id: int) -> Appointment | None: ...

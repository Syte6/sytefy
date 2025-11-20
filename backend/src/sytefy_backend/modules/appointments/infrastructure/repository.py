"""Repository implementation for appointments."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from sytefy_backend.modules.appointments.application.interfaces import IAppointmentRepository
from sytefy_backend.modules.appointments.domain.entities import Appointment
from sytefy_backend.modules.appointments.infrastructure.models import AppointmentModel


def _serialize_channels(channels: tuple[str, ...]) -> list[str]:
    return list(channels)


def _parse_channels(payload) -> tuple[str, ...]:
    if not payload:
        return tuple()
    return tuple(payload)


def _normalize(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _to_entity(model: AppointmentModel) -> Appointment:
    return Appointment(
        id=model.id,
        user_id=model.user_id,
        customer_id=model.customer_id,
        title=model.title,
        description=model.description,
        location=model.location,
        channel=model.channel,
        start_at=_normalize(model.start_at),
        end_at=_normalize(model.end_at),
        remind_at=_normalize(model.remind_at),
        reminder_channels=_parse_channels(model.reminder_channels),
        reminder_task_id=model.reminder_task_id,
        status=model.status,
        created_at=_normalize(model.created_at),
        updated_at=_normalize(model.updated_at),
    )


class AppointmentRepository(IAppointmentRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, appointment: Appointment) -> Appointment:
        model = AppointmentModel(
            user_id=appointment.user_id,
            customer_id=appointment.customer_id,
            title=appointment.title,
            description=appointment.description,
            location=appointment.location,
            channel=appointment.channel,
            start_at=appointment.start_at,
            end_at=appointment.end_at,
            remind_at=appointment.remind_at,
            reminder_channels=_serialize_channels(appointment.reminder_channels),
            reminder_task_id=appointment.reminder_task_id,
            status=appointment.status,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def list_by_user(
        self,
        *,
        user_id: int,
        status: str | None = None,
        start_from: datetime | None = None,
        start_to: datetime | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Appointment]:
        count_stmt = select(func.count()).select_from(AppointmentModel).where(AppointmentModel.user_id == user_id)
        stmt: Select[AppointmentModel] = select(AppointmentModel).where(AppointmentModel.user_id == user_id)
        if status:
            stmt = stmt.where(AppointmentModel.status == status)
            count_stmt = count_stmt.where(AppointmentModel.status == status)
        if start_from:
            stmt = stmt.where(AppointmentModel.start_at >= start_from)
            count_stmt = count_stmt.where(AppointmentModel.start_at >= start_from)
        if start_to:
            stmt = stmt.where(AppointmentModel.start_at <= start_to)
            count_stmt = count_stmt.where(AppointmentModel.start_at <= start_to)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        stmt = stmt.order_by(AppointmentModel.start_at)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return total, [_to_entity(model) for model in models]

    async def update_reminder_metadata(
        self,
        *,
        appointment_id: int,
        remind_at: datetime | None,
        reminder_task_id: str | None,
        channels: tuple[str, ...],
    ) -> Appointment:
        model = await self._session.get(AppointmentModel, appointment_id)
        if not model:
            raise ValueError("Appointment not found")
        model.remind_at = remind_at
        model.reminder_task_id = reminder_task_id
        model.reminder_channels = _serialize_channels(channels)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def update(self, appointment: Appointment) -> Appointment:
        model = await self._session.get(AppointmentModel, appointment.id)
        if not model:
            raise ValueError("Appointment not found")
        model.title = appointment.title
        model.description = appointment.description
        model.location = appointment.location
        model.channel = appointment.channel
        model.start_at = appointment.start_at
        model.end_at = appointment.end_at
        model.status = appointment.status
        model.remind_at = appointment.remind_at
        model.reminder_task_id = appointment.reminder_task_id
        model.reminder_channels = _serialize_channels(appointment.reminder_channels)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def get_by_id(self, appointment_id: int) -> Appointment | None:
        model = await self._session.get(AppointmentModel, appointment_id)
        if not model:
            return None
        return _to_entity(model)

"""Appointments routes."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from sytefy_backend.config import get_settings
from sytefy_backend.core.database import get_db
from sytefy_backend.core.tasks import celery_app
from sytefy_backend.modules.auth.domain.entities import User
from sytefy_backend.modules.auth.web.router import get_current_user
from sytefy_backend.modules.appointments.application.interfaces import IAppointmentRepository
from sytefy_backend.modules.appointments.application.ics import generate_ics
from sytefy_backend.modules.appointments.application.reminders import ScheduleAppointmentReminder
from sytefy_backend.modules.appointments.application.use_cases import (
    CancelAppointment,
    CreateAppointment,
    ListAppointments,
    UpdateAppointment,
)
from sytefy_backend.modules.appointments.infrastructure.reminder_queue import CeleryReminderTaskClient
from sytefy_backend.modules.appointments.infrastructure.repository import AppointmentRepository
from sytefy_backend.modules.customers.infrastructure.repository import CustomerRepository
from sytefy_backend.modules.appointments.web.dto import AppointmentCreateRequest, AppointmentResponse, AppointmentUpdateRequest
from sytefy_backend.core.exceptions import ApplicationError

settings = get_settings()
router = APIRouter(prefix="/appointments", tags=["Appointments"])


async def get_repo(db: AsyncSession = Depends(get_db)) -> IAppointmentRepository:
    return AppointmentRepository(db)


def get_scheduler() -> ScheduleAppointmentReminder:
    client = CeleryReminderTaskClient(celery_app)
    return ScheduleAppointmentReminder(client, offset_minutes=settings.reminder_offset_minutes)


async def get_create_use_case(
    db: AsyncSession = Depends(get_db),
    scheduler: ScheduleAppointmentReminder = Depends(get_scheduler),
) -> CreateAppointment:
    repo = AppointmentRepository(db)
    customer_repo = CustomerRepository(db)
    return CreateAppointment(repo, scheduler, customer_repo=customer_repo)


def get_list_use_case(repo: IAppointmentRepository = Depends(get_repo)) -> ListAppointments:
    return ListAppointments(repo)


async def get_update_use_case(
    db: AsyncSession = Depends(get_db),
    scheduler: ScheduleAppointmentReminder = Depends(get_scheduler),
) -> UpdateAppointment:
    repo = AppointmentRepository(db)
    customer_repo = CustomerRepository(db)
    return UpdateAppointment(repo, scheduler, customer_repo=customer_repo)


def get_cancel_use_case(
    repo: IAppointmentRepository = Depends(get_repo),
    scheduler: ScheduleAppointmentReminder = Depends(get_scheduler),
) -> CancelAppointment:
    return CancelAppointment(repo, scheduler)


def _to_response(entity) -> AppointmentResponse:
    return AppointmentResponse(
        id=entity.id or 0,
        title=entity.title,
        description=entity.description,
        location=entity.location,
        channel=entity.channel,
        start_at=entity.start_at,
        end_at=entity.end_at,
        status=entity.status,
        remind_at=entity.remind_at,
        reminder_channels=list(entity.reminder_channels),
        customer_id=entity.customer_id,
        reminder_task_id=entity.reminder_task_id,
    )


def _handle_app_error(exc: ApplicationError) -> None:
    detail = getattr(exc, "detail", str(exc))
    raise HTTPException(status_code=exc.status_code, detail=detail)


@router.post("/", response_model=AppointmentResponse, status_code=201)
async def create_appointment(
    payload: AppointmentCreateRequest,
    current_user: User = Depends(get_current_user),
    use_case: CreateAppointment = Depends(get_create_use_case),
):
    try:
        result = await use_case(
            user_id=current_user.id or 0,
            user_email=current_user.email,
            customer_id=payload.customer_id,
            title=payload.title,
            description=payload.description,
            location=payload.location,
            channel=payload.channel,
            start_at=payload.start_at,
            end_at=payload.end_at,
            reminder_channels=payload.reminder_channels,
        )
    except ApplicationError as exc:
        _handle_app_error(exc)
    return _to_response(result.appointment)


@router.get("/")
async def list_appointments(
    current_user: User = Depends(get_current_user),
    use_case: ListAppointments = Depends(get_list_use_case),
    status: str | None = None,
    start_from: datetime | None = None,
    start_to: datetime | None = None,
    limit: int = 20,
    offset: int = 0,
):
    try:
        total, appointments = await use_case(
            user_id=current_user.id or 0,
            status=status,
            start_from=start_from,
            start_to=start_to,
            limit=limit,
            offset=offset,
        )
    except ApplicationError as exc:
        _handle_app_error(exc)
    return {
        "total": total,
        "items": [_to_response(app) for app in appointments],
    }


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    payload: AppointmentUpdateRequest,
    current_user: User = Depends(get_current_user),
    use_case: UpdateAppointment = Depends(get_update_use_case),
):
    try:
        updated = await use_case(
            appointment_id=appointment_id,
            user_id=current_user.id or 0,
            user_email=current_user.email,
            title=payload.title,
            description=payload.description,
            location=payload.location,
            channel=payload.channel,
            start_at=payload.start_at,
            end_at=payload.end_at,
            reminder_channels=payload.reminder_channels,
            status=payload.status,
        )
    except ApplicationError as exc:
        _handle_app_error(exc)
    return _to_response(updated)


@router.post("/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    use_case: CancelAppointment = Depends(get_cancel_use_case),
):
    try:
        cancelled = await use_case(appointment_id=appointment_id, user_id=current_user.id or 0)
    except ApplicationError as exc:
        _handle_app_error(exc)
    return _to_response(cancelled)


@router.get("/{appointment_id}/ics")
async def download_appointment_ics(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    repo: IAppointmentRepository = Depends(get_repo),
):
    appointment = await repo.get_by_id(appointment_id)
    if not appointment or appointment.user_id != (current_user.id or 0):
        raise HTTPException(status_code=404, detail="Randevu bulunamadı.")
    ics = generate_ics(
        appointment,
        domain=settings.host or "sytefy.local",
        product_name=settings.app_name,
    )
    filename = f"appointment-{appointment_id}.ics"
    return Response(
        content=ics,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )

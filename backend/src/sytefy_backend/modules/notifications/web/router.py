"""Notification routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from sytefy_backend.core.database import get_db
from sytefy_backend.modules.auth.domain.entities import User
from sytefy_backend.modules.auth.web.router import get_current_user, require_roles
from sytefy_backend.core.exceptions import ApplicationError
from sytefy_backend.modules.notifications.application.interfaces import INotificationRepository
from sytefy_backend.modules.notifications.application.use_cases import CreateNotification, ListNotifications, MarkNotificationRead
from sytefy_backend.modules.notifications.infrastructure.dispatcher import CeleryNotificationDispatcher
from sytefy_backend.modules.notifications.infrastructure.repository import NotificationRepository
from sytefy_backend.modules.notifications.web.dto import NotificationCreateRequest, NotificationResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def get_repo(db: AsyncSession = Depends(get_db)) -> INotificationRepository:
    return NotificationRepository(db)


def get_create_use_case(repo: INotificationRepository = Depends(get_repo)) -> CreateNotification:
    return CreateNotification(repo, dispatcher=CeleryNotificationDispatcher())


def get_list_use_case(repo: INotificationRepository = Depends(get_repo)) -> ListNotifications:
    return ListNotifications(repo)


def get_mark_read_use_case(repo: INotificationRepository = Depends(get_repo)) -> MarkNotificationRead:
    return MarkNotificationRead(repo)


def _to_response(notification) -> NotificationResponse:
    return NotificationResponse(
        id=notification.id or 0,
        title=notification.title,
        body=notification.body,
        channel=notification.channel,
        status=notification.status,
        read_at=notification.read_at,
        created_at=notification.created_at,
    )


@router.get("/", response_model=list[NotificationResponse])
async def list_notifications(
    current_user: User = Depends(get_current_user),
    use_case: ListNotifications = Depends(get_list_use_case),
    status_filter: str | None = None,
):
    notifications = await use_case(user_id=current_user.id or 0, status=status_filter)
    return [_to_response(item) for item in notifications]


@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    payload: NotificationCreateRequest,
    _: User = Depends(require_roles("owner", "admin")),
    use_case: CreateNotification = Depends(get_create_use_case),
):
    result = await use_case(
        user_id=payload.user_id,
        title=payload.title,
        body=payload.body,
        channel=payload.channel,
        status=payload.status or "pending",
    )
    return _to_response(result.notification)


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    use_case: MarkNotificationRead = Depends(get_mark_read_use_case),
):
    try:
        notification = await use_case(notification_id=notification_id, user_id=current_user.id or 0)
    except ApplicationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _to_response(notification)

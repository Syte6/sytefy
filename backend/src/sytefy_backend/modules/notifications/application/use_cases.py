"""Notification use cases."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from sytefy_backend.core.exceptions import ApplicationError
from sytefy_backend.modules.notifications.application.interfaces import INotificationRepository
from sytefy_backend.modules.notifications.domain.entities import Notification


class NotificationDispatcher:
    """Simple dispatcher abstraction."""

    def dispatch(self, notification: Notification) -> None:
        # Future: route to email/SMS providers.
        return None


@dataclass(slots=True)
class CreateNotificationResult:
    notification: Notification


class CreateNotification:
    def __init__(self, repo: INotificationRepository, dispatcher: NotificationDispatcher | None = None):
        self._repo = repo
        self._dispatcher = dispatcher or NotificationDispatcher()

    async def __call__(
        self,
        *,
        user_id: int,
        title: str,
        body: str,
        channel: str,
        status: str = "pending",
    ) -> CreateNotificationResult:
        if not title.strip():
            raise ApplicationError("Başlık zorunlu.")
        notification = Notification(
            id=None,
            user_id=user_id,
            title=title,
            body=body,
            channel=channel,
            status=status,
            read_at=None,
            created_at=None,
        )
        stored = await self._repo.create(notification)
        self._dispatcher.dispatch(stored)
        return CreateNotificationResult(notification=stored)


class ListNotifications:
    def __init__(self, repo: INotificationRepository):
        self._repo = repo

    async def __call__(self, *, user_id: int, status: str | None = None) -> list[Notification]:
        return await self._repo.list_for_user(user_id=user_id, status=status)


class MarkNotificationRead:
    def __init__(self, repo: INotificationRepository):
        self._repo = repo

    async def __call__(self, *, notification_id: int, user_id: int) -> Notification:
        try:
            return await self._repo.mark_read(notification_id=notification_id, user_id=user_id)
        except ValueError as exc:
            raise ApplicationError("Bildirim bulunamadı") from exc

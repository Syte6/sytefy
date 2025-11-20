"""Notification repository implementation."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sytefy_backend.modules.notifications.application.interfaces import INotificationRepository
from sytefy_backend.modules.notifications.domain.entities import Notification
from sytefy_backend.modules.notifications.infrastructure.models import NotificationModel


def _to_entity(model: NotificationModel) -> Notification:
    return Notification(
        id=model.id,
        user_id=model.user_id,
        title=model.title,
        body=model.body,
        channel=model.channel,
        status=model.status,
        read_at=model.read_at,
        created_at=model.created_at,
    )


class NotificationRepository(INotificationRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, notification: Notification) -> Notification:
        model = NotificationModel(
            user_id=notification.user_id,
            title=notification.title,
            body=notification.body,
            channel=notification.channel,
            status=notification.status,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def list_for_user(self, *, user_id: int, status: str | None = None) -> list[Notification]:
        stmt = select(NotificationModel).where(NotificationModel.user_id == user_id)
        if status:
            stmt = stmt.where(NotificationModel.status == status)
        stmt = stmt.order_by(NotificationModel.created_at.desc())
        result = await self._session.execute(stmt)
        return [_to_entity(model) for model in result.scalars().all()]

    async def mark_read(self, *, notification_id: int, user_id: int) -> Notification:
        model = await self._session.get(NotificationModel, notification_id)
        if not model or model.user_id != user_id:
            raise ValueError("Bildirim bulunamadı")
        model.status = "read"
        model.read_at = datetime.now(timezone.utc)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

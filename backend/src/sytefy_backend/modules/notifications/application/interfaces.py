"""Notification repository interfaces."""

from __future__ import annotations

from typing import Protocol

from sytefy_backend.modules.notifications.domain.entities import Notification


class INotificationRepository(Protocol):
    async def create(self, notification: Notification) -> Notification: ...

    async def list_for_user(self, *, user_id: int, status: str | None = None) -> list[Notification]: ...

    async def mark_read(self, *, notification_id: int, user_id: int) -> Notification: ...

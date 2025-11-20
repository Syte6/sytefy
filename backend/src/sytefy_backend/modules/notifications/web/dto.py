"""Notification DTOs."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from sytefy_backend.shared.validators import StrictModel


class NotificationCreateRequest(StrictModel):
    user_id: int
    title: str = Field(max_length=255)
    body: str = Field(max_length=4000)
    channel: str = Field(default="log", max_length=20)
    status: str | None = Field(default=None, max_length=20)


class NotificationResponse(StrictModel):
    id: int
    title: str
    body: str
    channel: str
    status: str
    read_at: datetime | None
    created_at: datetime | None

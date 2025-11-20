"""DTO'lar for appointments endpoints."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from sytefy_backend.shared.validators import StrictModel


class AppointmentCreateRequest(StrictModel):
    customer_id: int | None = None
    title: str = Field(max_length=255)
    description: str | None = Field(default=None)
    location: str | None = Field(default=None, max_length=255)
    channel: str = Field(default="in_person", max_length=20)
    start_at: datetime
    end_at: datetime
    reminder_channels: list[str] | None = None


class AppointmentResponse(StrictModel):
    id: int
    title: str
    description: str | None
    location: str | None
    channel: str
    start_at: datetime
    end_at: datetime
    status: str
    remind_at: datetime | None
    reminder_channels: list[str]
    customer_id: int | None
    reminder_task_id: str | None


class AppointmentUpdateRequest(StrictModel):
    title: str | None = Field(default=None, max_length=255)
    description: str | None = None
    location: str | None = Field(default=None, max_length=255)
    channel: str | None = Field(default=None, max_length=20)
    start_at: datetime | None = None
    end_at: datetime | None = None
    reminder_channels: list[str] | None = None
    status: str | None = None


class AppointmentListResponse(StrictModel):
    items: list[AppointmentResponse]
    total: int

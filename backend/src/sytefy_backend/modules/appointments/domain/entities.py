"""Appointment domain entities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, Sequence, Tuple


@dataclass(slots=True)
class Appointment:
    id: Optional[int]
    user_id: int
    customer_id: Optional[int]
    title: str
    description: Optional[str]
    location: Optional[str]
    channel: str
    start_at: datetime
    end_at: datetime
    remind_at: Optional[datetime]
    reminder_channels: Tuple[str, ...]
    reminder_task_id: Optional[str]
    status: str = "scheduled"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass(slots=True)
class AppointmentReminder:
    appointment_id: int
    remind_at: datetime
    channels: Sequence[str]
    payload: dict[str, Any] | None = None

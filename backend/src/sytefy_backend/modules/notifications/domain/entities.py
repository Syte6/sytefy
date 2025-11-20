"""Notification domain entity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Notification:
    id: Optional[int]
    user_id: int
    title: str
    body: str
    channel: str
    status: str
    read_at: Optional[datetime]
    created_at: Optional[datetime]

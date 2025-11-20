"""Service domain entity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Service:
    id: Optional[int]
    user_id: int
    name: str
    description: Optional[str]
    price_amount: float
    price_currency: str
    duration_minutes: int
    status: str = "active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

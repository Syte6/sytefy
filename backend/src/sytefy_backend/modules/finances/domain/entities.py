"""Invoice domain entity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Invoice:
    id: Optional[int]
    user_id: int
    customer_id: Optional[int]
    number: str
    title: str
    description: Optional[str]
    amount: float
    currency: str
    status: str
    due_date: datetime
    issued_at: datetime
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

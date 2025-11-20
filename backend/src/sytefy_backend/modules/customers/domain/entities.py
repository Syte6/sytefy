"""Customer domain entity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Customer:
    id: Optional[int]
    user_id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    notes: Optional[str]
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

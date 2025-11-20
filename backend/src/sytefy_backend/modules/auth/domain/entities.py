"""Domain entities for the Auth module."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class User:
    id: Optional[int]
    email: str
    username: str
    hashed_password: str
    is_active: bool = True
    role: str = "owner"
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(slots=True)
class Role:
    id: Optional[int]
    slug: str
    name: str
    description: Optional[str] = None
    is_assignable: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

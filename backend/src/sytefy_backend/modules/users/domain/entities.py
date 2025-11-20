"""User profile domain entity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class UserProfile:
    id: Optional[int]
    user_id: int
    full_name: Optional[str]
    phone: Optional[str]
    business_name: Optional[str]
    business_type: Optional[str]
    mfa_enabled: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

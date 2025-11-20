"""JWT utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from uuid import uuid4

from jose import JWTError, jwt

from sytefy_backend.config import get_settings

_settings = get_settings()


@dataclass(frozen=True)
class RefreshTokenPayload:
    token: str
    jti: str
    expires_at: datetime


def _timestamp(minutes: int = 0, days: int = 0) -> datetime:
    return datetime.now(tz=timezone.utc) + timedelta(minutes=minutes, days=days)


def create_access_token(*, subject: str, user_id: int, role: str) -> str:
    payload: dict[str, Any] = {
        "sub": subject,
        "uid": user_id,
        "role": role,
        "type": "access",
        "jti": str(uuid4()),
        "exp": _timestamp(minutes=_settings.access_token_ttl_minutes),
    }
    return jwt.encode(payload, _settings.secret_key, algorithm=_settings.jwt_algorithm)


def create_refresh_token(*, subject: str, user_id: int) -> RefreshTokenPayload:
    expires_at = _timestamp(days=_settings.refresh_token_ttl_days)
    jti = str(uuid4())
    payload: dict[str, Any] = {
        "sub": subject,
        "uid": user_id,
        "type": "refresh",
        "jti": jti,
        "exp": expires_at,
    }
    token = jwt.encode(payload, _settings.secret_key, algorithm=_settings.jwt_algorithm)
    return RefreshTokenPayload(token=token, jti=jti, expires_at=expires_at)


class TokenDecodeError(Exception):
    """Raised when JWT decoding fails."""


def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, _settings.secret_key, algorithms=[_settings.jwt_algorithm])
    except JWTError as exc:  # pragma: no cover - external library
        raise TokenDecodeError(str(exc)) from exc

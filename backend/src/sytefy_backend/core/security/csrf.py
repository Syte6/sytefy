"""Basic CSRF token helper."""

from __future__ import annotations

import secrets
from typing import Optional

from fastapi import HTTPException, Request, status


CSRF_COOKIE_NAME = "sytefy_csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def validate_csrf(request: Request) -> None:
    cookie = request.cookies.get(CSRF_COOKIE_NAME)
    header = request.headers.get(CSRF_HEADER_NAME)
    if not cookie or not header or cookie != header:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF doğrulaması başarısız")

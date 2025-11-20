"""Password hashing helpers."""

from __future__ import annotations

import bcrypt

MAX_BCRYPT_LENGTH = 72


def _normalize(password: str) -> bytes:
    secret = password.encode("utf-8")
    if len(secret) > MAX_BCRYPT_LENGTH:
        secret = secret[:MAX_BCRYPT_LENGTH]
    return secret


def hash_password(password: str) -> str:
    secret = _normalize(password)
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(secret, salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    secret = _normalize(password)
    return bcrypt.checkpw(secret, hashed.encode("utf-8"))

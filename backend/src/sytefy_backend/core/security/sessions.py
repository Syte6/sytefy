"""Refresh session store backends for JWT rotation."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Protocol

import structlog
from redis.asyncio import Redis


@dataclass
class RefreshSession:
    jti: str
    user_id: int
    expires_at: datetime


class SessionStore(Protocol):
    async def remember(self, *, jti: str, user_id: int, expires_at: datetime) -> None: ...

    async def is_active(self, jti: str) -> bool: ...

    async def revoke(self, jti: str) -> None: ...

    async def revoke_all_for_user(self, user_id: int) -> None: ...


class InMemoryRefreshSessionStore(SessionStore):
    def __init__(self):
        self._sessions: Dict[str, RefreshSession] = {}
        self._lock = asyncio.Lock()

    def _purge_expired(self) -> None:
        now = datetime.now(tz=timezone.utc)
        expired = [jti for jti, session in self._sessions.items() if session.expires_at <= now]
        for jti in expired:
            self._sessions.pop(jti, None)

    async def remember(self, *, jti: str, user_id: int, expires_at: datetime) -> None:
        async with self._lock:
            self._purge_expired()
            self._sessions[jti] = RefreshSession(jti=jti, user_id=user_id, expires_at=expires_at)

    async def is_active(self, jti: str) -> bool:
        async with self._lock:
            self._purge_expired()
            return jti in self._sessions

    async def revoke(self, jti: str) -> None:
        async with self._lock:
            self._sessions.pop(jti, None)

    async def revoke_all_for_user(self, user_id: int) -> None:
        async with self._lock:
            self._purge_expired()
            for key in list(self._sessions.keys()):
                if self._sessions[key].user_id == user_id:
                    self._sessions.pop(key, None)


class RedisRefreshSessionStore(SessionStore):
    """Redis tabanlı oturum deposu."""

    def __init__(self, redis: Redis, prefix: str = "refresh"):
        self._redis = redis
        self._prefix = prefix.rstrip(":")
        self._logger = structlog.get_logger("sytefy.sessions.redis")

    @staticmethod
    def _coerce_utc(expires_at: datetime) -> datetime:
        if expires_at.tzinfo is None:
            return expires_at.replace(tzinfo=timezone.utc)
        return expires_at.astimezone(timezone.utc)

    def _session_key(self, jti: str) -> str:
        return f"{self._prefix}:session:{jti}"

    def _user_key(self, user_id: int) -> str:
        return f"{self._prefix}:user:{user_id}"

    @staticmethod
    def _decode(value):
        if value is None:
            return None
        if isinstance(value, bytes):
            return value.decode()
        return value

    async def remember(self, *, jti: str, user_id: int, expires_at: datetime) -> None:
        expires_at = self._coerce_utc(expires_at)
        ttl = max(1, int((expires_at - datetime.now(timezone.utc)).total_seconds()))
        pipe = self._redis.pipeline(transaction=True)
        pipe.set(self._session_key(jti), str(user_id), ex=ttl)
        pipe.sadd(self._user_key(user_id), jti)
        pipe.expire(self._user_key(user_id), ttl)
        await pipe.execute()

    async def is_active(self, jti: str) -> bool:
        exists = await self._redis.exists(self._session_key(jti))
        return bool(exists)

    async def revoke(self, jti: str) -> None:
        key = self._session_key(jti)
        raw_user_id = await self._redis.get(key)
        user_id = self._decode(raw_user_id)
        pipe = self._redis.pipeline(transaction=True)
        pipe.delete(key)
        if user_id is not None:
            pipe.srem(self._user_key(int(user_id)), jti)
        await pipe.execute()

    async def revoke_all_for_user(self, user_id: int) -> None:
        key = self._user_key(user_id)
        members = await self._redis.smembers(key)
        if not members:
            return
        pipe = self._redis.pipeline(transaction=True)
        for member in members:
            decoded = self._decode(member)
            if decoded is None:
                continue
            pipe.delete(self._session_key(decoded))
        pipe.delete(key)
        await pipe.execute()


RefreshSessionStore = InMemoryRefreshSessionStore

__all__ = [
    "SessionStore",
    "RefreshSessionStore",
    "InMemoryRefreshSessionStore",
    "RedisRefreshSessionStore",
    "RefreshSession",
]

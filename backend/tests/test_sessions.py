from datetime import datetime, timedelta, timezone

import pytest
from fakeredis.aioredis import FakeRedis

from sytefy_backend.core.security.sessions import RedisRefreshSessionStore


@pytest.mark.asyncio
async def test_redis_session_store_lifecycle():
    redis = FakeRedis()
    store = RedisRefreshSessionStore(redis, prefix="test-refresh")
    expires = datetime.now(timezone.utc) + timedelta(minutes=5)

    await store.remember(jti="abc", user_id=42, expires_at=expires)
    assert await store.is_active("abc") is True

    await store.revoke("abc")
    assert await store.is_active("abc") is False


@pytest.mark.asyncio
async def test_redis_session_store_revoke_all_for_user():
    redis = FakeRedis()
    store = RedisRefreshSessionStore(redis, prefix="bulk")
    expires = datetime.now(timezone.utc) + timedelta(minutes=5)

    await store.remember(jti="jti-1", user_id=7, expires_at=expires)
    await store.remember(jti="jti-2", user_id=7, expires_at=expires)
    await store.remember(jti="jti-3", user_id=8, expires_at=expires)

    await store.revoke_all_for_user(7)
    assert await store.is_active("jti-1") is False
    assert await store.is_active("jti-2") is False
    assert await store.is_active("jti-3") is True

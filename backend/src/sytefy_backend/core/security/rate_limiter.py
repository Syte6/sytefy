"""Simple in-memory sliding window rate limiter."""

from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from dataclasses import dataclass
from time import monotonic
from typing import Deque, DefaultDict, Tuple


@dataclass(frozen=True)
class RateLimitConfig:
    requests: int
    period_seconds: int


class InMemoryRateLimiter:
    def __init__(self, config: RateLimitConfig):
        self._config = config
        self._buckets: DefaultDict[str, Deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def allow(self, key: str) -> Tuple[bool, float | None]:
        now = monotonic()
        async with self._lock:
            bucket = self._buckets[key]
            window_start = now - self._config.period_seconds
            while bucket and bucket[0] < window_start:
                bucket.popleft()
            if len(bucket) >= self._config.requests:
                retry_after = max(0.0, bucket[0] + self._config.period_seconds - now)
                return False, retry_after
            bucket.append(now)
            return True, None

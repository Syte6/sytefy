"""Security-focused FastAPI middleware."""

from __future__ import annotations

import uuid
from typing import Awaitable, Callable

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from sytefy_backend.core.logging import bind_request_id
from sytefy_backend.core.security.headers import SecurityHeadersConfig, apply_security_headers
from sytefy_backend.core.security.rate_limiter import InMemoryRateLimiter

RequestHandler = Callable[[Request], Awaitable[Response]]


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestHandler) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        bind_request_id(request_id)
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers.setdefault("X-Request-ID", request_id)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, config: SecurityHeadersConfig):
        super().__init__(app)
        self._config = config

    async def dispatch(self, request: Request, call_next: RequestHandler) -> Response:
        response = await call_next(request)
        apply_security_headers(response, self._config)
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limiter: InMemoryRateLimiter, identifier: str = "global"):
        super().__init__(app)
        self._limiter = limiter
        self._identifier = identifier

    async def dispatch(self, request: Request, call_next: RequestHandler) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        key = f"{self._identifier}:{client_ip}:{request.method}:{request.url.path}"
        allowed, retry_after = await self._limiter.allow(key)
        if not allowed:
            headers = {"Retry-After": str(int(retry_after or 0))}
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="İstek sınırı aşıldı.",
                headers=headers,
            )
        return await call_next(request)

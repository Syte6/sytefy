"""FastAPI entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sytefy_backend.config import get_settings
from sytefy_backend.core.logging import configure_logging
from sytefy_backend.core.observability import MetricsRecorder, ObservabilityMiddleware, metrics_endpoint
from sytefy_backend.core.security import (
    InMemoryRateLimiter,
    RateLimitConfig,
    RateLimitMiddleware,
    RequestContextMiddleware,
    SecurityHeadersConfig,
    SecurityHeadersMiddleware,
)
from sytefy_backend.modules import api_router

settings = get_settings()
configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
    limiter = InMemoryRateLimiter(
        RateLimitConfig(
            requests=settings.rate_limit_requests,
            period_seconds=settings.rate_limit_period_seconds,
        )
    )
    app.add_middleware(RateLimitMiddleware, limiter=limiter)
    app.add_middleware(
        SecurityHeadersMiddleware,
        config=SecurityHeadersConfig(
            content_security_policy=settings.csp,
            strict_transport_security=settings.hsts,
            referrer_policy=settings.referrer_policy,
        ),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
        allow_credentials=settings.cors_allow_credentials,
    )
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(ObservabilityMiddleware, recorder=MetricsRecorder())

    app.include_router(api_router)
    @app.get("/api/health")
    async def health_check():
        return {"status": "ok"}
    app.add_api_route("/metrics", metrics_endpoint, methods=["GET"], include_in_schema=False)
    return app


app = create_app()

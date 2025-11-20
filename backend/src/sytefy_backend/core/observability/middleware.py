"""Gözlemlenebilirlik middleware'i."""

from __future__ import annotations

import time

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from sytefy_backend.core.logging import get_request_id
from sytefy_backend.core.observability.metrics import MetricsRecorder, resolve_path_template


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """İstek metriklerini toplayıp yapılandırılmış log yazar."""

    def __init__(self, app, recorder: MetricsRecorder):
        super().__init__(app)
        self._recorder = recorder
        self._logger = structlog.get_logger("sytefy.observability")

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        status_code = 500
        try:
            response: Response = await call_next(request)
            status_code = response.status_code
        except Exception:
            duration = time.perf_counter() - start
            self._recorder.record(request=request, status_code=status_code, duration_seconds=duration)
            self._logger.exception(
                "request.failed",
                method=request.method,
                path=resolve_path_template(request),
                status_code=status_code,
                duration_ms=duration * 1000,
                request_id=get_request_id(),
            )
            raise
        duration = time.perf_counter() - start
        self._recorder.record(request=request, status_code=status_code, duration_seconds=duration)
        self._logger.info(
            "request.completed",
            method=request.method,
            path=resolve_path_template(request),
            status_code=status_code,
            duration_ms=duration * 1000,
            request_id=get_request_id(),
        )
        return response


__all__ = ["ObservabilityMiddleware"]

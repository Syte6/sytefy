"""Prometheus metrik yardımcıları."""

from __future__ import annotations

from typing import Final

from fastapi import Request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import Response

RequestCounter: Final = Counter(
    "sytefy_requests_total",
    "Toplam HTTP istek sayısı.",
    labelnames=("method", "path", "status"),
)
RequestLatency: Final = Histogram(
    "sytefy_request_duration_seconds",
    "HTTP istek süreleri.",
    labelnames=("method", "path"),
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)


def resolve_path_template(request: Request) -> str:
    route = request.scope.get("route")
    if route and getattr(route, "path", None):
        return route.path  # type: ignore[return-value]
    return request.url.path


class MetricsRecorder:
    """HTTP metriklerini kaydeder."""

    def __init__(self, counter: Counter = RequestCounter, latency: Histogram = RequestLatency) -> None:
        self._counter = counter
        self._latency = latency

    def record(self, *, request: Request, status_code: int, duration_seconds: float) -> None:
        path = resolve_path_template(request)
        labels = {
            "method": request.method,
            "path": path,
        }
        self._counter.labels(**labels, status=str(status_code)).inc()
        self._latency.labels(**labels).observe(duration_seconds)


def metrics_endpoint() -> Response:
    """Prometheus uyumlu metrik çıktısı döndürür."""
    payload = generate_latest()
    return Response(content=payload, media_type=CONTENT_TYPE_LATEST)


__all__ = ["MetricsRecorder", "metrics_endpoint", "resolve_path_template"]

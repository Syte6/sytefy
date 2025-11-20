"""Celery uygulaması yapılandırması."""

from __future__ import annotations

from functools import lru_cache

from celery import Celery

from sytefy_backend.config import get_settings

CELERY_IMPORTS = (
    "sytefy_backend.modules.appointments.tasks",
    "sytefy_backend.modules.notifications.tasks",
)


@lru_cache(maxsize=1)
def create_celery_app() -> Celery:
    settings = get_settings()
    app = Celery(
        "sytefy_backend",
        broker=settings.celery_broker_url or settings.redis_url,
        backend=settings.celery_result_backend or settings.redis_url,
        include=CELERY_IMPORTS,
    )
    app.conf.update(
        task_always_eager=settings.celery_task_always_eager,
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        enable_utc=True,
        timezone="UTC",
        task_default_retry_delay=60,
    )
    return app


celery_app = create_celery_app()

__all__ = ["celery_app", "create_celery_app"]

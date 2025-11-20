"""Celery worker entrypoint."""

from sytefy_backend.core.tasks import celery_app

__all__ = ["celery_app"]

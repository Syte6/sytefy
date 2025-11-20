"""Prometheus metrikleri için Celery yardımcıları."""

from __future__ import annotations

from prometheus_client import Counter

ReminderTaskCounter = Counter(
    "sytefy_reminder_tasks_total",
    "Celery reminder görevlerinin durum dağılımı.",
    labelnames=("status",),
)
ReminderChannelCounter = Counter(
    "sytefy_reminder_channel_events_total",
    "Kanal bazlı reminder teslimat sonuçları.",
    labelnames=("channel", "status"),
)


def record_reminder_task_outcome(status: str) -> None:
    ReminderTaskCounter.labels(status=status).inc()


def record_reminder_channel_event(channel: str, status: str) -> None:
    ReminderChannelCounter.labels(channel=channel, status=status).inc()


__all__ = [
    "ReminderTaskCounter",
    "ReminderChannelCounter",
    "record_reminder_task_outcome",
    "record_reminder_channel_event",
]

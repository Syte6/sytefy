from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import httpx
from prometheus_client import REGISTRY

from sytefy_backend.core.observability import celery_metrics
from sytefy_backend.core.tasks.celery_app import celery_app
from sytefy_backend.modules.appointments import tasks as reminder_tasks
from sytefy_backend.modules.appointments.application.reminders import ReminderScheduled, ScheduleAppointmentReminder
from sytefy_backend.modules.appointments.infrastructure.reminder_queue import CeleryReminderTaskClient
from sytefy_backend.modules.appointments.tasks import send_appointment_reminder
from sytefy_backend.modules.notifications.infrastructure import channels


def test_schedule_appointment_reminder_executes_task_eagerly():
    client = CeleryReminderTaskClient(celery_app)
    use_case = ScheduleAppointmentReminder(task_client=client, offset_minutes=30)
    appointment_time = datetime.now(timezone.utc) + timedelta(hours=2)

    result = use_case(appointment_id=123, appointment_time=appointment_time, channels=["log"])

    assert isinstance(result, ReminderScheduled)
    assert result.appointment_id == 123
    assert result.remind_at <= appointment_time
    assert isinstance(result.task_id, str)


def test_schedule_reminder_clamps_past_times():
    client = CeleryReminderTaskClient(celery_app)
    use_case = ScheduleAppointmentReminder(task_client=client, offset_minutes=60)
    appointment_time = datetime.now(timezone.utc) + timedelta(minutes=10)

    result = use_case(appointment_id=1, appointment_time=appointment_time)
    now = datetime.now(timezone.utc)
    assert result.remind_at >= now - timedelta(seconds=1)


def test_send_appointment_reminder_delivers_channels(monkeypatch):
    monkeypatch.setenv("NOTIFICATION_SMS_ENABLED", "true")
    monkeypatch.setenv("NOTIFICATION_SMS_ACCOUNT_SID", "AC123")
    monkeypatch.setenv("NOTIFICATION_SMS_AUTH_TOKEN", "token")
    monkeypatch.setenv("NOTIFICATION_SMS_FROM", "+18885550100")
    monkeypatch.setenv("NOTIFICATION_SMS_BASE_URL", "https://api.test.twilio.com")
    monkeypatch.setenv("NOTIFICATION_EMAIL_HOST", "smtp.test")
    monkeypatch.setenv("NOTIFICATION_EMAIL_PORT", "2525")
    monkeypatch.setenv("NOTIFICATION_EMAIL_USERNAME", "user")
    monkeypatch.setenv("NOTIFICATION_EMAIL_PASSWORD", "pass")
    monkeypatch.setenv("NOTIFICATION_EMAIL_USE_TLS", "true")
    monkeypatch.setenv("NOTIFICATION_EMAIL_USE_SSL", "false")
    remind_at = datetime.now(timezone.utc).isoformat()

    class DummySMTP:
        sent_messages: list = []

        def __init__(self, host, port, timeout=None):
            self.host = host
            self.port = port
            self.timeout = timeout

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def ehlo(self):
            return True

        def starttls(self):
            return True

        def login(self, username, password):
            self.username = username
            self.password = password

        def send_message(self, message):
            DummySMTP.sent_messages.append(message)

    monkeypatch.setattr(channels, "smtplib", SimpleNamespace(SMTP=DummySMTP, SMTP_SSL=DummySMTP))

    def fake_post(url, data, auth=None, timeout=None):
        fake_post.called = True
        request = httpx.Request("POST", url)
        return httpx.Response(201, json={"sid": "SM123"}, request=request)

    fake_post.called = False
    monkeypatch.setattr(channels, "httpx", SimpleNamespace(post=fake_post))

    recorded_notifications: list[dict] = []

    def fake_persist_notification(**kwargs):
        recorded_notifications.append(kwargs)

    monkeypatch.setattr(reminder_tasks, "_persist_notification", fake_persist_notification)

    def metric_value(name: str, labels: dict[str, str]) -> float:
        value = REGISTRY.get_sample_value(name, labels)
        return value or 0.0

    email_before = metric_value(
        "sytefy_reminder_channel_events_total",
        {"channel": "email", "status": "sent"},
    )
    sms_before = metric_value(
        "sytefy_reminder_channel_events_total",
        {"channel": "sms", "status": "sent"},
    )
    task_success_before = metric_value(
        "sytefy_reminder_tasks_total",
        {"status": "succeeded"},
    )
    task_start_before = metric_value(
        "sytefy_reminder_tasks_total",
        {"status": "started"},
    )

    task_ctx = SimpleNamespace(request=SimpleNamespace(id="test-task"))
    raw_task = send_appointment_reminder.__wrapped__
    bound = raw_task.__get__(task_ctx, type(task_ctx))
    result = bound(
        appointment_id=5,
        remind_at=remind_at,
        channels=["email", "sms", "log"],
        context={
            "title": "Kontrol",
            "user_id": 99,
            "user_email": "owner@example.com",
            "customer_email": "customer@example.com",
            "customer_phone": "+15555550123",
        },
    )
    delivered = set(result["delivered"])
    assert {"email", "sms", "log"}.issubset(delivered)
    assert DummySMTP.sent_messages, "email should be sent via SMTP backend"
    assert fake_post.called is True
    assert {item["channel"] for item in recorded_notifications} == {"email", "sms"}
    assert all(item["status"] == "sent" for item in recorded_notifications)
    assert metric_value(
        "sytefy_reminder_channel_events_total",
        {"channel": "email", "status": "sent"},
    ) == email_before + 1
    assert metric_value(
        "sytefy_reminder_channel_events_total",
        {"channel": "sms", "status": "sent"},
    ) == sms_before + 1
    assert metric_value(
        "sytefy_reminder_tasks_total",
        {"status": "succeeded"},
    ) == task_success_before + 1
    assert metric_value(
        "sytefy_reminder_tasks_total",
        {"status": "started"},
    ) == task_start_before + 1

"""ICS export helpers for appointments."""

from __future__ import annotations

from datetime import datetime, timezone

from sytefy_backend.modules.appointments.domain.entities import Appointment


def _format_dt(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y%m%dT%H%M%SZ")


def _escape_text(value: str | None) -> str:
    if not value:
        return ""
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace(",", "\\,").replace(";", "\\;")


def generate_ics(appointment: Appointment, *, domain: str = "sytefy.local", product_name: str = "Sytefy") -> str:
    """Create VCALENDAR string for given appointment."""
    now = datetime.now(timezone.utc)
    uid = f"appointment-{appointment.id}@{domain}"
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:-//{product_name}//Appointments//TR",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{_format_dt(now)}",
        f"DTSTART:{_format_dt(appointment.start_at)}",
        f"DTEND:{_format_dt(appointment.end_at)}",
        f"SUMMARY:{_escape_text(appointment.title)}",
    ]
    if appointment.description:
        lines.append(f"DESCRIPTION:{_escape_text(appointment.description)}")
    if appointment.location:
        lines.append(f"LOCATION:{_escape_text(appointment.location)}")
    lines.extend(
        [
            "END:VEVENT",
            "END:VCALENDAR",
        ]
    )
    return "\r\n".join(lines) + "\r\n"


__all__ = ["generate_ics"]

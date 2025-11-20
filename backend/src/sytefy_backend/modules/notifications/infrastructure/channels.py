"""Notification channel services for email/SMS delivery."""

from __future__ import annotations

from email.message import EmailMessage
import smtplib
from typing import Callable, Protocol

import httpx
import structlog


logger = structlog.get_logger("sytefy.notifications")


class EmailBackend(Protocol):
    def send(self, message: EmailMessage) -> None: ...


class SMTPEmailBackend:
    """Simple SMTP backend that supports TLS/SSL."""

    def __init__(
        self,
        *,
        host: str,
        port: int,
        username: str | None = None,
        password: str | None = None,
        use_tls: bool = True,
        use_ssl: bool = False,
        timeout: float = 10.0,
    ):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._use_tls = use_tls
        self._use_ssl = use_ssl
        self._timeout = timeout

    def send(self, message: EmailMessage) -> None:
        smtp_cls = smtplib.SMTP_SSL if self._use_ssl else smtplib.SMTP
        with smtp_cls(self._host, self._port, timeout=self._timeout) as server:
            server.ehlo()
            if self._use_tls and not self._use_ssl:
                server.starttls()
                server.ehlo()
            if self._username and self._password:
                server.login(self._username, self._password)
            server.send_message(message)


class EmailNotificationService:
    """Email sender that prefers SMTP but falls back to structured logging."""

    def __init__(
        self,
        *,
        sender: str,
        enabled: bool = True,
        backend: EmailBackend | None = None,
        host: str | None = None,
        port: int = 587,
        username: str | None = None,
        password: str | None = None,
        use_tls: bool = True,
        use_ssl: bool = False,
        timeout: float = 10.0,
    ):
        self._sender = sender
        self._enabled = enabled
        self._logger = structlog.get_logger("sytefy.notifications.email")
        self._backend = backend
        if backend is None and host:
            self._backend = SMTPEmailBackend(
                host=host,
                port=port,
                username=username,
                password=password,
                use_tls=use_tls,
                use_ssl=use_ssl,
                timeout=timeout,
            )

    def send(self, *, recipient: str | None, subject: str, body: str) -> bool:
        if not recipient:
            self._logger.warning("email_missing_recipient", subject=subject)
            return False
        if not self._enabled:
            self._logger.info("email_disabled", recipient=recipient, subject=subject)
            return False
        if not self._backend:
            self._logger.info(
                "email_backend_missing",
                sender=self._sender,
                recipient=recipient,
                subject=subject,
                body=body,
            )
            return False
        message = EmailMessage()
        message["From"] = self._sender
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)
        try:
            self._backend.send(message)
        except Exception as exc:  # pragma: no cover - defensive logging path
            self._logger.exception(
                "email_send_failed",
                recipient=recipient,
                subject=subject,
                exc=exc,
            )
            return False
        self._logger.info("email_sent", recipient=recipient, subject=subject)
        return True


class SMSBackend(Protocol):
    def send(self, *, to: str, body: str) -> dict | None: ...


class TwilioSMSBackend:
    """Twilio REST client wrapper (sync)."""

    def __init__(
        self,
        *,
        account_sid: str,
        auth_token: str,
        from_number: str,
        base_url: str = "https://api.twilio.com",
        timeout: float = 10.0,
        request_func: Callable[..., httpx.Response] | None = None,
    ):
        self._account_sid = account_sid
        self._auth_token = auth_token
        self._from = from_number
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._request = request_func or httpx.post

    def send(self, *, to: str, body: str) -> dict:
        url = f"{self._base_url}/2010-04-01/Accounts/{self._account_sid}/Messages.json"
        response = self._request(
            url,
            data={
                "To": to,
                "From": self._from,
                "Body": body,
            },
            auth=(self._account_sid, self._auth_token),
            timeout=self._timeout,
        )
        response.raise_for_status()
        return response.json()


class SMSNotificationService:
    """SMS sender with Twilio backend + logging fallback."""

    def __init__(
        self,
        *,
        sender: str,
        enabled: bool = False,
        backend: SMSBackend | None = None,
    ):
        self._sender = sender
        self._enabled = enabled
        self._backend = backend
        self._logger = structlog.get_logger("sytefy.notifications.sms")

    def send(self, *, recipient: str | None, body: str) -> bool:
        if not recipient:
            self._logger.warning("sms_missing_recipient")
            return False
        if not self._enabled:
            self._logger.info("sms_disabled", recipient=recipient)
            return False
        if not self._backend:
            self._logger.info(
                "sms_backend_missing",
                sender=self._sender,
                recipient=recipient,
                body=body,
            )
            return False
        try:
            self._backend.send(to=recipient, body=body)
        except Exception as exc:  # pragma: no cover - defensive logging path
            self._logger.exception(
                "sms_send_failed",
                recipient=recipient,
                exc=exc,
            )
            return False
        self._logger.info("sms_sent", recipient=recipient)
        return True


__all__ = [
    "EmailNotificationService",
    "SMSNotificationService",
    "SMTPEmailBackend",
    "TwilioSMSBackend",
]

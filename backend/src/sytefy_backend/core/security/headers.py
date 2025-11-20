"""Security header policies."""

from dataclasses import dataclass
from starlette.responses import Response


@dataclass(frozen=True)
class SecurityHeadersConfig:
    content_security_policy: str
    strict_transport_security: str
    referrer_policy: str
    frame_options: str = "DENY"
    xss_protection: str = "1; mode=block"
    content_type_options: str = "nosniff"
    permissions_policy: str = "geolocation=(), microphone=(), camera=()"


def apply_security_headers(response: Response, config: SecurityHeadersConfig) -> None:
    headers = {
        "Content-Security-Policy": config.content_security_policy,
        "Strict-Transport-Security": config.strict_transport_security,
        "Referrer-Policy": config.referrer_policy,
        "X-Frame-Options": config.frame_options,
        "X-Content-Type-Options": config.content_type_options,
        "X-XSS-Protection": config.xss_protection,
        "Permissions-Policy": config.permissions_policy,
    }
    for key, value in headers.items():
        response.headers.setdefault(key, value)

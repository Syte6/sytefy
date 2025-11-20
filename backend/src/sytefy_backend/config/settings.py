"""Application settings driven by environment variables."""

import json
from typing import List, Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = Field(default="Sytefy API")
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    # Security
    secret_key: str = Field(default="change-me")
    jwt_algorithm: str = Field(default="HS256")
    access_token_ttl_minutes: int = Field(default=15)
    refresh_token_ttl_days: int = Field(default=7)
    password_min_length: int = Field(default=12)

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://sytefy:sytefy@localhost:5432/sytefy"
    )
    echo_sql: bool = Field(default=False)

    # Redis / cache
    redis_url: str = Field(default="redis://localhost:6379/0")
    celery_broker_url: str | None = Field(default=None)
    celery_result_backend: str | None = Field(default=None)

    # CORS / Security headers
    cors_allowed_origins_raw: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        alias="CORS_ALLOWED_ORIGINS",
    )
    cors_allow_methods: list[str] = Field(default_factory=lambda: ["GET", "POST", "PUT", "PATCH", "DELETE"])
    cors_allow_headers: list[str] = Field(default_factory=lambda: ["*"])
    cors_allow_credentials: bool = Field(default=True)

    csp: str = Field(
        default="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:"
    )
    hsts: str = Field(default="max-age=63072000; includeSubDomains; preload")
    referrer_policy: str = Field(default="no-referrer")

    rate_limit_requests: int = Field(default=100)
    rate_limit_period_seconds: int = Field(default=60)

    # Cookie / session
    access_cookie_name: str = Field(default="sytefy_access_token")
    refresh_cookie_name: str = Field(default="sytefy_refresh_token")
    cookie_domain: str | None = Field(default=None)
    cookie_secure: bool = Field(default=False)
    cookie_samesite: str = Field(default="lax")
    cookie_path: str = Field(default="/")
    enable_csrf_protection: bool = Field(default=False)
    session_store_backend: Literal["memory", "redis"] = Field(default="memory")
    redis_session_prefix: str = Field(default="refresh")
    celery_task_always_eager: bool = Field(default=True)
    reminder_offset_minutes: int = Field(default=30)
    reminder_max_retries: int = Field(default=3)
    notification_email_from: str = Field(default="no-reply@sytefy.local")
    notification_email_enabled: bool = Field(default=True)
    notification_email_host: str | None = Field(default=None)
    notification_email_port: int = Field(default=587)
    notification_email_username: str | None = Field(default=None)
    notification_email_password: str | None = Field(default=None)
    notification_email_use_tls: bool = Field(default=True)
    notification_email_use_ssl: bool = Field(default=False)
    notification_email_timeout: float = Field(default=10.0)
    notification_sms_from: str = Field(default="Sytefy")
    notification_sms_enabled: bool = Field(default=False)
    notification_sms_account_sid: str | None = Field(default=None)
    notification_sms_auth_token: str | None = Field(default=None)
    notification_sms_base_url: str = Field(default="https://api.twilio.com")
    notification_sms_timeout: float = Field(default=10.0)

    @property
    def cors_allowed_origins(self) -> List[str]:
        raw = self.cors_allowed_origins_raw.strip()
        if not raw:
            return []
        if raw.startswith("["):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [str(origin).strip() for origin in parsed if str(origin).strip()]
            except json.JSONDecodeError:
                pass
        return [origin.strip() for origin in raw.split(",") if origin.strip()]

    @field_validator("database_url", mode="before")
    @classmethod
    def ensure_async_driver(cls, value: str) -> str:
        if value.startswith("postgresql+psycopg://"):
            return value.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value

    @property
    def database_url_sync(self) -> str:
        if self.database_url.startswith("postgresql+asyncpg://"):
            return self.database_url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
        return self.database_url

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    return Settings()

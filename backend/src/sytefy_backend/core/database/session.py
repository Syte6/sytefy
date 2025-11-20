"""Database session/engine helpers."""

from __future__ import annotations

from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from sytefy_backend.config import get_settings


def _ensure_async_url(url: str) -> str:
    if url.startswith("postgresql+psycopg://"):
        return url.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


_settings = get_settings()
_engine: AsyncEngine = create_async_engine(
    _ensure_async_url(_settings.database_url),
    echo=_settings.echo_sql,
)
_SessionLocal = async_sessionmaker(
    bind=_engine,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with _SessionLocal() as session:
        yield session


__all__ = ["get_db", "_engine", "_SessionLocal"]

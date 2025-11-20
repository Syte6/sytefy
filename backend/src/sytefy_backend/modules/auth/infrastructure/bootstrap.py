"""RBAC bootstrapping yardımcıları."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from sytefy_backend.modules.auth.infrastructure.repositories import RoleRepository


async def ensure_roles(session: AsyncSession) -> None:
    """Varsayılan roller yoksa oluştur."""
    repo = RoleRepository(session)
    await repo.ensure_builtin()


__all__ = ["ensure_roles"]

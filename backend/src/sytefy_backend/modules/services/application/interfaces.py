"""Repository interfaces for services."""

from __future__ import annotations

from typing import Protocol

from sytefy_backend.modules.services.domain.entities import Service


class IServiceRepository(Protocol):
    async def create(self, service: Service) -> Service: ...

    async def update(self, service: Service) -> Service: ...

    async def delete(self, service_id: int, user_id: int) -> None: ...

    async def list_by_user(self, *, user_id: int, status: str | None = None) -> list[Service]: ...

    async def get_by_id(self, service_id: int) -> Service | None: ...

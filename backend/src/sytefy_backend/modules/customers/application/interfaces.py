"""Interfaces for customers module."""

from __future__ import annotations

from typing import Protocol, Sequence

from sytefy_backend.modules.customers.domain.entities import Customer


class ICustomerRepository(Protocol):
    async def list(self, *, user_id: int, limit: int = 100, offset: int = 0) -> Sequence[Customer]: ...

    async def create(
        self,
        *,
        user_id: int,
        name: str,
        email: str | None,
        phone: str | None,
        notes: str | None,
    ) -> Customer: ...

    async def get_by_id(self, customer_id: int) -> Customer | None: ...

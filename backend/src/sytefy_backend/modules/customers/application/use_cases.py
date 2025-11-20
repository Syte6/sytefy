"""Use cases for customers."""

from __future__ import annotations

from typing import Sequence

from sytefy_backend.modules.customers.application.interfaces import ICustomerRepository
from sytefy_backend.modules.customers.domain.entities import Customer


class ListCustomers:
    def __init__(self, repo: ICustomerRepository):
        self._repo = repo

    async def __call__(self, *, user_id: int, limit: int = 100, offset: int = 0) -> Sequence[Customer]:
        return await self._repo.list(user_id=user_id, limit=limit, offset=offset)


class CreateCustomer:
    def __init__(self, repo: ICustomerRepository):
        self._repo = repo

    async def __call__(
        self,
        *,
        user_id: int,
        name: str,
        email: str | None,
        phone: str | None,
        notes: str | None,
    ) -> Customer:
        return await self._repo.create(
            user_id=user_id,
            name=name,
            email=email,
            phone=phone,
            notes=notes,
        )

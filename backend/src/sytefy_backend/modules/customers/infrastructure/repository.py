"""Repository implementation for customers."""

from __future__ import annotations

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sytefy_backend.modules.customers.application.interfaces import ICustomerRepository
from sytefy_backend.modules.customers.domain.entities import Customer
from sytefy_backend.modules.customers.infrastructure.models import CustomerModel


def _to_entity(model: CustomerModel) -> Customer:
    return Customer(
        id=model.id,
        user_id=model.user_id,
        name=model.name,
        email=model.email,
        phone=model.phone,
        notes=model.notes,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class CustomerRepository(ICustomerRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list(self, *, user_id: int, limit: int = 100, offset: int = 0) -> Sequence[Customer]:
        query = (
            select(CustomerModel)
            .where(CustomerModel.user_id == user_id, CustomerModel.is_active.is_(True))
            .offset(offset)
            .limit(limit)
            .order_by(CustomerModel.created_at.desc())
        )
        result = await self._session.execute(query)
        return [_to_entity(row) for row in result.scalars().all()]

    async def create(
        self,
        *,
        user_id: int,
        name: str,
        email: str | None,
        phone: str | None,
        notes: str | None,
    ) -> Customer:
        model = CustomerModel(
            user_id=user_id,
            name=name,
            email=email,
            phone=phone,
            notes=notes,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def get_by_id(self, customer_id: int) -> Customer | None:
        model = await self._session.get(CustomerModel, customer_id)
        if not model:
            return None
        return _to_entity(model)

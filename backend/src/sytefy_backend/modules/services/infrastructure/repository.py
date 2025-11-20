"""Repository implementation for services."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sytefy_backend.modules.services.application.interfaces import IServiceRepository
from sytefy_backend.modules.services.domain.entities import Service
from sytefy_backend.modules.services.infrastructure.models import ServiceModel


def _to_entity(model: ServiceModel) -> Service:
    return Service(
        id=model.id,
        user_id=model.user_id,
        name=model.name,
        description=model.description,
        price_amount=model.price_amount,
        price_currency=model.price_currency,
        duration_minutes=model.duration_minutes,
        status=model.status,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class ServiceRepository(IServiceRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, service: Service) -> Service:
        model = ServiceModel(
            user_id=service.user_id,
            name=service.name,
            description=service.description,
            price_amount=service.price_amount,
            price_currency=service.price_currency,
            duration_minutes=service.duration_minutes,
            status=service.status,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def update(self, service: Service) -> Service:
        model = await self._session.get(ServiceModel, service.id)
        if not model:
            raise ValueError("Service not found")
        model.name = service.name
        model.description = service.description
        model.price_amount = service.price_amount
        model.price_currency = service.price_currency
        model.duration_minutes = service.duration_minutes
        model.status = service.status
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def delete(self, service_id: int, user_id: int) -> None:
        model = await self._session.get(ServiceModel, service_id)
        if model and model.user_id == user_id:
            await self._session.delete(model)
            await self._session.commit()

    async def list_by_user(self, *, user_id: int, status: str | None = None) -> list[Service]:
        stmt = select(ServiceModel).where(ServiceModel.user_id == user_id)
        if status:
            stmt = stmt.where(ServiceModel.status == status)
        result = await self._session.execute(stmt.order_by(ServiceModel.name))
        models = result.scalars().all()
        return [_to_entity(model) for model in models]

    async def get_by_id(self, service_id: int) -> Service | None:
        model = await self._session.get(ServiceModel, service_id)
        return _to_entity(model) if model else None

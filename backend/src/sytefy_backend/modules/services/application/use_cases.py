"""Service use cases."""

from __future__ import annotations

from dataclasses import dataclass

from sytefy_backend.core.exceptions import ApplicationError
from sytefy_backend.modules.services.application.interfaces import IServiceRepository
from sytefy_backend.modules.services.domain.entities import Service


@dataclass(slots=True)
class CreateServiceResult:
    service: Service


class CreateService:
    def __init__(self, repo: IServiceRepository):
        self._repo = repo

    async def __call__(
        self,
        *,
        user_id: int,
        name: str,
        description: str | None,
        price_amount: float,
        price_currency: str,
        duration_minutes: int,
    ) -> CreateServiceResult:
        if price_amount <= 0:
            raise ApplicationError("Tutar 0'dan büyük olmalı.")
        if duration_minutes <= 0:
            raise ApplicationError("Süre 0'dan büyük olmalı.")
        service = Service(
            id=None,
            user_id=user_id,
            name=name,
            description=description,
            price_amount=price_amount,
            price_currency=price_currency,
            duration_minutes=duration_minutes,
        )
        stored = await self._repo.create(service)
        return CreateServiceResult(service=stored)


class ListServices:
    def __init__(self, repo: IServiceRepository):
        self._repo = repo

    async def __call__(self, *, user_id: int, status: str | None = None) -> list[Service]:
        return await self._repo.list_by_user(user_id=user_id, status=status)


class UpdateService:
    def __init__(self, repo: IServiceRepository):
        self._repo = repo

    async def __call__(
        self,
        *,
        service_id: int,
        user_id: int,
        name: str | None,
        description: str | None,
        price_amount: float | None,
        price_currency: str | None,
        duration_minutes: int | None,
        status: str | None,
    ) -> Service:
        existing = await self._repo.get_by_id(service_id)
        if not existing or existing.user_id != user_id:
            raise ApplicationError("Hizmet bulunamadı")
        if name is not None:
            existing.name = name
        if description is not None:
            existing.description = description
        if price_amount is not None:
            if price_amount <= 0:
                raise ApplicationError("Tutar 0'dan büyük olmalı.")
            existing.price_amount = price_amount
        if price_currency is not None:
            existing.price_currency = price_currency
        if duration_minutes is not None:
            if duration_minutes <= 0:
                raise ApplicationError("Süre 0'dan büyük olmalı.")
            existing.duration_minutes = duration_minutes
        if status is not None:
            existing.status = status
        return await self._repo.update(existing)


class DeleteService:
    def __init__(self, repo: IServiceRepository):
        self._repo = repo

    async def __call__(self, *, service_id: int, user_id: int) -> None:
        await self._repo.delete(service_id, user_id)

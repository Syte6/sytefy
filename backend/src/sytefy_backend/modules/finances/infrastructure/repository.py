"""Invoice repository implementation."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sytefy_backend.modules.finances.application.interfaces import IInvoiceRepository
from sytefy_backend.modules.finances.domain.entities import Invoice
from sytefy_backend.modules.finances.infrastructure.models import InvoiceModel


def _normalize(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _to_entity(model: InvoiceModel) -> Invoice:
    return Invoice(
        id=model.id,
        user_id=model.user_id,
        customer_id=model.customer_id,
        number=model.number,
        title=model.title,
        description=model.description,
        amount=float(model.amount),
        currency=model.currency,
        status=model.status,
        due_date=_normalize(model.due_date),
        issued_at=_normalize(model.issued_at),
        created_at=_normalize(model.created_at) if model.created_at else None,
        updated_at=_normalize(model.updated_at) if model.updated_at else None,
    )


class InvoiceRepository(IInvoiceRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, invoice: Invoice) -> Invoice:
        model = InvoiceModel(
            user_id=invoice.user_id,
            customer_id=invoice.customer_id,
            number=invoice.number,
            title=invoice.title,
            description=invoice.description,
            amount=invoice.amount,
            currency=invoice.currency,
            status=invoice.status,
            due_date=invoice.due_date,
            issued_at=invoice.issued_at,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def list_by_user(self, *, user_id: int, status: str | None = None) -> list[Invoice]:
        stmt = select(InvoiceModel).where(InvoiceModel.user_id == user_id).order_by(InvoiceModel.due_date.desc())
        if status:
            stmt = stmt.where(InvoiceModel.status == status)
        result = await self._session.execute(stmt)
        return [_to_entity(model) for model in result.scalars().all()]

    async def get_by_id(self, invoice_id: int) -> Invoice | None:
        model = await self._session.get(InvoiceModel, invoice_id)
        if not model:
            return None
        return _to_entity(model)

    async def update(self, invoice: Invoice) -> Invoice:
        model = await self._session.get(InvoiceModel, invoice.id)
        if not model:
            raise ValueError("Invoice not found")
        model.title = invoice.title
        model.description = invoice.description
        model.amount = invoice.amount
        model.currency = invoice.currency
        model.status = invoice.status
        model.due_date = invoice.due_date
        model.issued_at = invoice.issued_at
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def delete(self, invoice_id: int, user_id: int) -> None:
        model = await self._session.get(InvoiceModel, invoice_id)
        if not model or model.user_id != user_id:
            raise ValueError("Invoice not found")
        await self._session.delete(model)
        await self._session.commit()

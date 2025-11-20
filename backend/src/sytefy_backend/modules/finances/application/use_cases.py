"""Invoice use cases."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sytefy_backend.core.exceptions import ApplicationError
from sytefy_backend.modules.finances.application.interfaces import IInvoiceRepository
from sytefy_backend.modules.finances.domain.entities import Invoice

ALLOWED_STATUSES = {"draft", "sent", "paid", "void"}


def _ensure_amount(amount: float | None) -> float:
    if amount is None or amount <= 0:
        raise ApplicationError("Tutar 0'dan büyük olmalı.")
    return amount


def _ensure_due_date(due_date: datetime) -> datetime:
    if due_date.tzinfo is None:
        due_date = due_date.replace(tzinfo=timezone.utc)
    else:
        due_date = due_date.astimezone(timezone.utc)
    return due_date


def _normalize_status(status: str | None) -> str:
    value = (status or "draft").lower()
    if value not in ALLOWED_STATUSES:
        raise ApplicationError("Geçersiz fatura statüsü.")
    return value


def _ensure_issued_at(issued_at: datetime | None) -> datetime:
    if not issued_at:
        return datetime.now(timezone.utc)
    if issued_at.tzinfo is None:
        return issued_at.replace(tzinfo=timezone.utc)
    return issued_at.astimezone(timezone.utc)


def _generate_number(user_id: int, issued_at: datetime) -> str:
    return f"INV-{user_id}-{issued_at.strftime('%Y%m%d%H%M%S')}"


@dataclass(slots=True)
class CreateInvoiceResult:
    invoice: Invoice


class CreateInvoice:
    def __init__(self, repo: IInvoiceRepository):
        self._repo = repo

    async def __call__(
        self,
        *,
        user_id: int,
        title: str,
        amount: float,
        currency: str,
        due_date: datetime,
        customer_id: int | None = None,
        description: str | None = None,
        number: str | None = None,
        issued_at: datetime | None = None,
        status: str | None = None,
    ) -> CreateInvoiceResult:
        if not title.strip():
            raise ApplicationError("Başlık zorunlu.")
        amount = _ensure_amount(amount)
        due_date = _ensure_due_date(due_date)
        issued_at = _ensure_issued_at(issued_at)
        if due_date < issued_at:
            raise ApplicationError("Vade tarihi düzenlenme tarihinden önce olamaz.")
        status_value = _normalize_status(status)
        invoice = Invoice(
            id=None,
            user_id=user_id,
            customer_id=customer_id,
            number=number or _generate_number(user_id, issued_at),
            title=title,
            description=description,
            amount=amount,
            currency=currency,
            status=status_value,
            due_date=due_date,
            issued_at=issued_at,
        )
        stored = await self._repo.create(invoice)
        return CreateInvoiceResult(invoice=stored)


class ListInvoices:
    def __init__(self, repo: IInvoiceRepository):
        self._repo = repo

    async def __call__(self, *, user_id: int, status: str | None = None) -> list[Invoice]:
        status_value = status.lower() if status else None
        if status_value and status_value not in ALLOWED_STATUSES:
            raise ApplicationError("Geçersiz fatura statüsü.")
        return await self._repo.list_by_user(user_id=user_id, status=status_value)


class UpdateInvoice:
    def __init__(self, repo: IInvoiceRepository):
        self._repo = repo

    async def __call__(
        self,
        *,
        invoice_id: int,
        user_id: int,
        title: str | None = None,
        description: str | None = None,
        amount: float | None = None,
        currency: str | None = None,
        due_date: datetime | None = None,
        status: str | None = None,
    ) -> Invoice:
        existing = await self._repo.get_by_id(invoice_id)
        if not existing or existing.user_id != user_id:
            raise ApplicationError("Fatura bulunamadı.")
        if title is not None:
            if not title.strip():
                raise ApplicationError("Başlık boş olamaz.")
            existing.title = title
        if description is not None:
            existing.description = description
        if amount is not None:
            existing.amount = _ensure_amount(amount)
        if currency is not None:
            existing.currency = currency
        if due_date is not None:
            normalized = _ensure_due_date(due_date)
            if normalized < existing.issued_at:
                raise ApplicationError("Vade tarihi düzenlenme tarihinden önce olamaz.")
            existing.due_date = normalized
        if status is not None:
            existing.status = _normalize_status(status)
        return await self._repo.update(existing)


class DeleteInvoice:
    def __init__(self, repo: IInvoiceRepository):
        self._repo = repo

    async def __call__(self, *, invoice_id: int, user_id: int) -> None:
        await self._repo.delete(invoice_id, user_id)

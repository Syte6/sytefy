"""Repository interfaces for finance invoices."""

from __future__ import annotations

from typing import Protocol

from sytefy_backend.modules.finances.domain.entities import Invoice


class IInvoiceRepository(Protocol):
    async def create(self, invoice: Invoice) -> Invoice: ...

    async def list_by_user(self, *, user_id: int, status: str | None = None) -> list[Invoice]: ...

    async def get_by_id(self, invoice_id: int) -> Invoice | None: ...

    async def update(self, invoice: Invoice) -> Invoice: ...

    async def delete(self, invoice_id: int, user_id: int) -> None: ...

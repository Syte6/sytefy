"""DTOs for invoices."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from sytefy_backend.shared.validators import StrictModel


class InvoiceCreateRequest(StrictModel):
    title: str = Field(max_length=255)
    amount: float
    currency: str = Field(default="TRY", max_length=8)
    due_date: datetime
    customer_id: int | None = None
    description: str | None = Field(default=None)
    number: str | None = Field(default=None, max_length=64)
    issued_at: datetime | None = None
    status: str | None = Field(default=None, max_length=20)


class InvoiceResponse(StrictModel):
    id: int
    number: str
    title: str
    description: str | None
    amount: float
    currency: str
    status: str
    due_date: datetime
    issued_at: datetime
    customer_id: int | None
    created_at: datetime | None
    updated_at: datetime | None


class InvoiceUpdateRequest(StrictModel):
    title: str | None = Field(default=None, max_length=255)
    description: str | None = None
    amount: float | None = None
    currency: str | None = Field(default=None, max_length=8)
    due_date: datetime | None = None
    status: str | None = Field(default=None, max_length=20)

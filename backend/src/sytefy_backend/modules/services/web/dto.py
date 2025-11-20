"""DTOs for services endpoints."""

from __future__ import annotations

from pydantic import Field

from sytefy_backend.shared.validators import StrictModel


class ServiceCreateRequest(StrictModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    price_amount: float = Field(gt=0)
    price_currency: str = Field(default="TRY", max_length=10)
    duration_minutes: int = Field(gt=0, le=600)


class ServiceUpdateRequest(StrictModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    price_amount: float | None = Field(default=None, gt=0)
    price_currency: str | None = Field(default=None, max_length=10)
    duration_minutes: int | None = Field(default=None, gt=0, le=600)
    status: str | None = None


class ServiceResponse(StrictModel):
    id: int
    name: str
    description: str | None
    price_amount: float
    price_currency: str
    duration_minutes: int
    status: str

"""DTOs for customer routes."""

from pydantic import EmailStr, Field

from sytefy_backend.shared.validators import StrictModel


class CustomerCreateRequest(StrictModel):
    name: str = Field(min_length=2, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    notes: str | None = Field(default=None, max_length=500)


class CustomerResponse(StrictModel):
    id: int
    name: str
    email: EmailStr | None
    phone: str | None
    notes: str | None

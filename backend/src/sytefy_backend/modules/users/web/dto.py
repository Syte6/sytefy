"""DTOs for user profile endpoints."""

from pydantic import Field

from sytefy_backend.shared.validators import StrictModel


class UserProfileUpdateRequest(StrictModel):
    full_name: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    business_name: str | None = Field(default=None, max_length=255)
    business_type: str | None = Field(default=None, max_length=100)
    mfa_enabled: bool | None = Field(default=None)


class UserProfileResponse(StrictModel):
    id: int | None
    full_name: str | None
    phone: str | None
    business_name: str | None
    business_type: str | None
    mfa_enabled: bool


class AdminUserResponse(StrictModel):
    id: int
    email: str
    username: str
    role: str
    is_active: bool
    mfa_enabled: bool


class UpdateUserRoleRequest(StrictModel):
    role: str = Field(max_length=50)


class UpdateUserMfaRequest(StrictModel):
    enabled: bool


class RoleResponse(StrictModel):
    slug: str
    name: str
    description: str | None
    is_assignable: bool

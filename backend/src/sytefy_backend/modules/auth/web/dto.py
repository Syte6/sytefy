"""Request/response DTOs for auth endpoints."""

from pydantic import EmailStr, Field

from sytefy_backend.shared.validators import StrictModel


class RegisterRequest(StrictModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=12, max_length=128)


class LoginRequest(StrictModel):
    email: EmailStr
    password: str = Field(min_length=12)


class TokenResponse(StrictModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(StrictModel):
    id: int
    email: EmailStr
    username: str
    role: str


class RefreshTokenRequest(StrictModel):
    refresh_token: str | None = None

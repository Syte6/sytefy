"""Interfaces for auth module dependencies."""

from __future__ import annotations

from typing import Protocol

from sytefy_backend.modules.auth.domain.entities import User
from sytefy_backend.core.security.tokens import RefreshTokenPayload


class IUserRepository(Protocol):
    async def get_by_id(self, user_id: int) -> User | None: ...

    async def get_by_email(self, email: str) -> User | None: ...

    async def get_by_username(self, username: str) -> User | None: ...

    async def create(self, user: User) -> User: ...

    async def list_all(self) -> list[User]: ...

    async def update_role(self, user_id: int, role: str) -> User: ...


class IPasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...

    def verify(self, password: str, hashed: str) -> bool: ...


class ITokenService(Protocol):
    def create_access_token(self, *, subject: str, user_id: int, role: str) -> str: ...

    def create_refresh_token(self, *, subject: str, user_id: int) -> RefreshTokenPayload: ...

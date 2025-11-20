"""Interfaces for user profiles ve admin kullanıcı işlemleri."""

from __future__ import annotations

from typing import Protocol

from sytefy_backend.modules.auth.domain.entities import Role, User
from sytefy_backend.modules.users.domain.entities import UserProfile


class IUserProfileRepository(Protocol):
    async def get_by_user_id(self, user_id: int) -> UserProfile | None: ...

    async def create_or_update(self, profile: UserProfile) -> UserProfile: ...

    async def list_all(self) -> list[UserProfile]: ...


class IUserAccountRepository(Protocol):
    async def list_all(self) -> list[User]: ...

    async def update_role(self, user_id: int, role: str) -> User: ...

    async def get_by_id(self, user_id: int) -> User | None: ...


class IRoleCatalog(Protocol):
    async def list_assignable(self) -> list[Role]: ...

    async def get(self, slug: str) -> Role | None: ...

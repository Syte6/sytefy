"""Use cases for user profiles."""

from __future__ import annotations

from sytefy_backend.modules.users.application.interfaces import IUserProfileRepository
from sytefy_backend.modules.users.domain.entities import UserProfile


class GetUserProfile:
    def __init__(self, repo: IUserProfileRepository):
        self._repo = repo

    async def __call__(self, *, user_id: int) -> UserProfile | None:
        return await self._repo.get_by_user_id(user_id)


class UpdateUserProfile:
    def __init__(self, repo: IUserProfileRepository):
        self._repo = repo

    async def __call__(
        self,
        *,
        user_id: int,
        full_name: str | None,
        phone: str | None,
        business_name: str | None,
        business_type: str | None,
        mfa_enabled: bool | None,
    ) -> UserProfile:
        existing = await self._repo.get_by_user_id(user_id) or UserProfile(
            id=None,
            user_id=user_id,
            full_name=None,
            phone=None,
            business_name=None,
            business_type=None,
        )
        existing.full_name = full_name
        existing.phone = phone
        existing.business_name = business_name
        existing.business_type = business_type
        if mfa_enabled is not None:
            existing.mfa_enabled = mfa_enabled
        return await self._repo.create_or_update(existing)

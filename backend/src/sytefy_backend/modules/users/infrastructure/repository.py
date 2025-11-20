"""Repository for user profiles."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sytefy_backend.modules.users.application.interfaces import IUserProfileRepository
from sytefy_backend.modules.users.domain.entities import UserProfile
from sytefy_backend.modules.users.infrastructure.models import UserProfileModel


def _to_entity(model: UserProfileModel) -> UserProfile:
    return UserProfile(
        id=model.id,
        user_id=model.user_id,
        full_name=model.full_name,
        phone=model.phone,
        business_name=model.business_name,
        business_type=model.business_type,
        mfa_enabled=model.mfa_enabled,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class UserProfileRepository(IUserProfileRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_user_id(self, user_id: int) -> UserProfile | None:
        result = await self._session.execute(select(UserProfileModel).where(UserProfileModel.user_id == user_id))
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def create_or_update(self, profile: UserProfile) -> UserProfile:
        model = None
        if profile.id:
            model = await self._session.get(UserProfileModel, profile.id)
        if not model:
            model = UserProfileModel(user_id=profile.user_id)

        model.full_name = profile.full_name
        model.phone = profile.phone
        model.business_name = profile.business_name
        model.business_type = profile.business_type
        model.mfa_enabled = profile.mfa_enabled

        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def list_all(self) -> list[UserProfile]:
        result = await self._session.execute(select(UserProfileModel))
        models = result.scalars().all()
        return [_to_entity(model) for model in models]

"""Admin kullanıcı işlemleri için use-case'ler."""

from __future__ import annotations

from dataclasses import dataclass

from sytefy_backend.core.exceptions import ApplicationError
from sytefy_backend.modules.auth.domain.entities import User
from sytefy_backend.modules.users.application.interfaces import IRoleCatalog, IUserAccountRepository, IUserProfileRepository
from sytefy_backend.modules.users.domain.entities import UserProfile


@dataclass(slots=True)
class AdminUserView:
    id: int
    email: str
    username: str
    role: str
    is_active: bool
    mfa_enabled: bool


def _merge(user: User, profile: UserProfile | None) -> AdminUserView:
    return AdminUserView(
        id=user.id or 0,
        email=user.email,
        username=user.username,
        role=user.role,
        is_active=user.is_active,
        mfa_enabled=profile.mfa_enabled if profile else False,
    )


class ListUserAccounts:
    def __init__(self, user_repo: IUserAccountRepository, profile_repo: IUserProfileRepository):
        self._user_repo = user_repo
        self._profile_repo = profile_repo

    async def __call__(self) -> list[AdminUserView]:
        users = await self._user_repo.list_all()
        profiles = await self._profile_repo.list_all()
        profile_map = {profile.user_id: profile for profile in profiles}
        return [_merge(user, profile_map.get(user.id or 0)) for user in users]


class UpdateUserRole:
    def __init__(self, user_repo: IUserAccountRepository, roles: IRoleCatalog, profile_repo: IUserProfileRepository):
        self._user_repo = user_repo
        self._roles = roles
        self._profiles = profile_repo

    async def __call__(self, *, user_id: int, role: str) -> AdminUserView:
        role_entity = await self._roles.get(role)
        if not role_entity or (not role_entity.is_assignable and role_entity.slug != "owner"):
            raise ApplicationError("Rol bulunamadı veya atanamaz.")
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise ApplicationError("Kullanıcı bulunamadı.")
        if user.role == "owner" and role != "owner":
            # İlk sahip güvenliğini koru
            owners = [u for u in await self._user_repo.list_all() if u.role == "owner"]
            if len(owners) <= 1:
                raise ApplicationError("Son sahibi düşüremezsiniz.")
        updated = await self._user_repo.update_role(user_id, role_entity.slug)
        profile = await self._profiles.get_by_user_id(user_id)
        return _merge(updated, profile)


class UpdateUserMfa:
    def __init__(self, profile_repo: IUserProfileRepository, user_repo: IUserAccountRepository):
        self._profiles = profile_repo
        self._users = user_repo

    async def __call__(self, *, user_id: int, enabled: bool) -> AdminUserView:
        user = await self._users.get_by_id(user_id)
        if not user:
            raise ApplicationError("Kullanıcı bulunamadı.")
        profile = await self._profiles.get_by_user_id(user_id) or UserProfile(
            id=None,
            user_id=user_id,
            full_name=None,
            phone=None,
            business_name=None,
            business_type=None,
        )
        profile.mfa_enabled = enabled
        stored = await self._profiles.create_or_update(profile)
        return _merge(user, stored)


__all__ = ["AdminUserView", "ListUserAccounts", "UpdateUserRole", "UpdateUserMfa"]

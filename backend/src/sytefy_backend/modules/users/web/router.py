"""User profile + admin kullanıcı routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from sytefy_backend.core.database import get_db
from sytefy_backend.modules.auth.web.router import get_current_user, get_role_repo, get_user_repo, require_roles
from sytefy_backend.modules.auth.domain.entities import User
from sytefy_backend.modules.auth.infrastructure.repositories import RoleRepository, UserRepository
from sytefy_backend.modules.users.application.use_cases import GetUserProfile, UpdateUserProfile
from sytefy_backend.modules.users.application.admin_use_cases import ListUserAccounts, UpdateUserMfa, UpdateUserRole
from sytefy_backend.modules.users.infrastructure.repository import UserProfileRepository
from sytefy_backend.modules.users.web.dto import (
    AdminUserResponse,
    RoleResponse,
    UpdateUserMfaRequest,
    UpdateUserRoleRequest,
    UserProfileResponse,
    UserProfileUpdateRequest,
)

router = APIRouter(prefix="/users", tags=["Users"])


async def get_profile_repo(db: AsyncSession = Depends(get_db)) -> UserProfileRepository:
    return UserProfileRepository(db)


def get_get_profile_use_case(repo: UserProfileRepository = Depends(get_profile_repo)) -> GetUserProfile:
    return GetUserProfile(repo)


def get_update_profile_use_case(repo: UserProfileRepository = Depends(get_profile_repo)) -> UpdateUserProfile:
    return UpdateUserProfile(repo)


def get_admin_list_use_case(
    user_repo: UserRepository = Depends(get_user_repo),
    profile_repo: UserProfileRepository = Depends(get_profile_repo),
) -> ListUserAccounts:
    return ListUserAccounts(user_repo, profile_repo)


def get_update_role_use_case(
    user_repo: UserRepository = Depends(get_user_repo),
    role_repo: RoleRepository = Depends(get_role_repo),
    profile_repo: UserProfileRepository = Depends(get_profile_repo),
) -> UpdateUserRole:
    return UpdateUserRole(user_repo, role_repo, profile_repo)


def get_update_mfa_use_case(
    profile_repo: UserProfileRepository = Depends(get_profile_repo),
    user_repo: UserRepository = Depends(get_user_repo),
) -> UpdateUserMfa:
    return UpdateUserMfa(profile_repo, user_repo)


@router.get("/me", response_model=UserProfileResponse)
async def get_me_profile(
    current_user: User = Depends(get_current_user),
    use_case: GetUserProfile = Depends(get_get_profile_use_case),
):
    profile = await use_case(user_id=current_user.id or 0)
    return UserProfileResponse(
        id=profile.id if profile else None,
        full_name=profile.full_name if profile else None,
        phone=profile.phone if profile else None,
        business_name=profile.business_name if profile else None,
        business_type=profile.business_type if profile else None,
        mfa_enabled=profile.mfa_enabled if profile else False,
    )


@router.put("/me", response_model=UserProfileResponse)
async def update_me_profile(
    payload: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    use_case: UpdateUserProfile = Depends(get_update_profile_use_case),
):
    if current_user.id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Kullanıcı kimliği eksik")
    profile = await use_case(
        user_id=current_user.id,
        full_name=payload.full_name,
        phone=payload.phone,
        business_name=payload.business_name,
        business_type=payload.business_type,
        mfa_enabled=payload.mfa_enabled,
    )
    return UserProfileResponse(
        id=profile.id,
        full_name=profile.full_name,
        phone=profile.phone,
        business_name=profile.business_name,
        business_type=profile.business_type,
        mfa_enabled=profile.mfa_enabled,
    )


@router.get("/admin/roles", response_model=list[RoleResponse])
async def list_assignable_roles(
    _: User = Depends(require_roles("owner", "admin")),
    role_repo: RoleRepository = Depends(get_role_repo),
):
    roles = await role_repo.list_assignable()
    return [
        RoleResponse(slug=role.slug, name=role.name, description=role.description, is_assignable=role.is_assignable)
        for role in roles
    ]


@router.get("/admin/accounts", response_model=list[AdminUserResponse])
async def list_user_accounts(
    _: User = Depends(require_roles("owner", "admin")),
    use_case: ListUserAccounts = Depends(get_admin_list_use_case),
):
    users = await use_case()
    return [
        AdminUserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            role=user.role,
            is_active=user.is_active,
            mfa_enabled=user.mfa_enabled,
        )
        for user in users
    ]


@router.patch("/admin/accounts/{user_id}/role", response_model=AdminUserResponse)
async def update_user_role(
    user_id: int,
    payload: UpdateUserRoleRequest,
    _: User = Depends(require_roles("owner")),
    use_case: UpdateUserRole = Depends(get_update_role_use_case),
):
    result = await use_case(user_id=user_id, role=payload.role)
    return AdminUserResponse(
        id=result.id,
        email=result.email,
        username=result.username,
        role=result.role,
        is_active=result.is_active,
        mfa_enabled=result.mfa_enabled,
    )


@router.patch("/admin/accounts/{user_id}/mfa", response_model=AdminUserResponse)
async def update_user_mfa(
    user_id: int,
    payload: UpdateUserMfaRequest,
    _: User = Depends(require_roles("owner", "admin")),
    use_case: UpdateUserMfa = Depends(get_update_mfa_use_case),
):
    result = await use_case(user_id=user_id, enabled=payload.enabled)
    return AdminUserResponse(
        id=result.id,
        email=result.email,
        username=result.username,
        role=result.role,
        is_active=result.is_active,
        mfa_enabled=result.mfa_enabled,
    )

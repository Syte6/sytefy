"""SQLAlchemy repository for users and roles."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sytefy_backend.modules.auth.application.interfaces import IUserRepository
from sytefy_backend.modules.auth.domain.entities import Role, User
from sytefy_backend.modules.auth.domain.roles import BUILTIN_ROLES
from .models import RoleModel, UserModel


def _to_entity(model: UserModel) -> User:
    return User(
        id=model.id,
        email=model.email,
        username=model.username,
        hashed_password=model.hashed_password,
        role=model.role,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _role_to_entity(model: RoleModel) -> Role:
    return Role(
        id=model.id,
        slug=model.slug,
        name=model.name,
        description=model.description,
        is_assignable=model.is_assignable,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.email == email))
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def get_by_username(self, username: str) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.username == username))
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def create(self, user: User) -> User:
        model = UserModel(
            email=user.email,
            username=user.username,
            hashed_password=user.hashed_password,
            role=user.role,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def list_all(self) -> list[User]:
        result = await self._session.execute(select(UserModel).order_by(UserModel.id))
        models = result.scalars().all()
        return [_to_entity(model) for model in models]

    async def update_role(self, user_id: int, role: str) -> User:
        model = await self._session.get(UserModel, user_id)
        if not model:
            raise ValueError("Kullanıcı bulunamadı")
        model.role = role
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)


class RoleRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_assignable(self) -> list[Role]:
        result = await self._session.execute(select(RoleModel).where(RoleModel.is_assignable.is_(True)).order_by(RoleModel.name))
        models = result.scalars().all()
        return [_role_to_entity(model) for model in models]

    async def get(self, slug: str) -> Role | None:
        result = await self._session.execute(select(RoleModel).where(RoleModel.slug == slug))
        model = result.scalar_one_or_none()
        return _role_to_entity(model) if model else None

    async def ensure_builtin(self) -> None:
        result = await self._session.execute(select(RoleModel.slug))
        existing_slugs = set(result.scalars().all())
        created = False
        for role in BUILTIN_ROLES:
            if role.slug in existing_slugs:
                continue
            self._session.add(
                RoleModel(
                    slug=role.slug,
                    name=role.name,
                    description=role.description,
                    is_assignable=role.is_assignable,
                )
            )
            created = True
        if created:
            await self._session.commit()

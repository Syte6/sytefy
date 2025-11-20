"""Auth use cases."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sytefy_backend.modules.auth.domain.entities import User
from sytefy_backend.modules.auth.application.interfaces import IUserRepository, IPasswordHasher, ITokenService
from sytefy_backend.core.exceptions import ApplicationError


@dataclass(frozen=True)
class AuthResult:
    user: User
    access_token: str
    refresh_token: str
    refresh_jti: str
    refresh_expires_at: datetime


class RegisterUser:
    def __init__(self, repo: IUserRepository, hasher: IPasswordHasher):
        self._repo = repo
        self._hasher = hasher

    async def __call__(self, *, email: str, username: str, password: str) -> User:
        if await self._repo.get_by_email(email):
            raise ApplicationError("Email zaten kayıtlı.")
        if await self._repo.get_by_username(username):
            raise ApplicationError("Kullanıcı adı kullanımda.")
        hashed = self._hasher.hash(password)
        user = User(id=None, email=email, username=username, hashed_password=hashed)
        return await self._repo.create(user)


class AuthenticateUser:
    def __init__(self, repo: IUserRepository, hasher: IPasswordHasher, tokens: ITokenService):
        self._repo = repo
        self._hasher = hasher
        self._tokens = tokens

    async def __call__(self, *, email: str, password: str) -> AuthResult:
        user = await self._repo.get_by_email(email)
        if not user or not self._hasher.verify(password, user.hashed_password):
            raise ApplicationError("Kimlik doğrulama başarısız.")
        if not user.is_active:
            raise ApplicationError("Hesap devre dışı.")
        access = self._tokens.create_access_token(subject=user.email, user_id=user.id or 0, role=user.role)
        refresh_payload = self._tokens.create_refresh_token(subject=user.email, user_id=user.id or 0)
        return AuthResult(
            user=user,
            access_token=access,
            refresh_token=refresh_payload.token,
            refresh_jti=refresh_payload.jti,
            refresh_expires_at=refresh_payload.expires_at,
        )

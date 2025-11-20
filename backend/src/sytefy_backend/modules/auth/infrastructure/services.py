"""Infrastructure services for auth module."""

from sytefy_backend.core.security import passwords
from sytefy_backend.core.security import tokens
from sytefy_backend.modules.auth.application.interfaces import IPasswordHasher, ITokenService


class BcryptPasswordHasher(IPasswordHasher):
    def hash(self, password: str) -> str:
        return passwords.hash_password(password)

    def verify(self, password: str, hashed: str) -> bool:
        return passwords.verify_password(password, hashed)


class JwtTokenService(ITokenService):
    def create_access_token(self, *, subject: str, user_id: int, role: str) -> str:
        return tokens.create_access_token(subject=subject, user_id=user_id, role=role)

    def create_refresh_token(self, *, subject: str, user_id: int):
        return tokens.create_refresh_token(subject=subject, user_id=user_id)

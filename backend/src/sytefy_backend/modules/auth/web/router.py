"""Auth HTTP routes."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from sytefy_backend.config import get_settings
from sytefy_backend.core.database import get_db
from redis.asyncio import Redis

from sytefy_backend.core.security.sessions import (
    InMemoryRefreshSessionStore,
    RedisRefreshSessionStore,
    SessionStore,
)
from sytefy_backend.core.security.tokens import TokenDecodeError, decode_token
from sytefy_backend.core.security.csrf import CSRF_COOKIE_NAME, generate_csrf_token, validate_csrf
from sytefy_backend.modules.auth.application.use_cases import AuthenticateUser, RegisterUser
from sytefy_backend.modules.auth.domain.entities import User
from sytefy_backend.modules.auth.infrastructure.repositories import RoleRepository, UserRepository
from sytefy_backend.modules.auth.infrastructure.services import BcryptPasswordHasher, JwtTokenService
from sytefy_backend.modules.auth.web.dto import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Auth"])
_session_store: SessionStore | None = None
_redis_client: Redis | None = None


async def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    role_repo = RoleRepository(db)
    await role_repo.ensure_builtin()
    return UserRepository(db)


async def get_role_repo(db: AsyncSession = Depends(get_db)) -> RoleRepository:
    repo = RoleRepository(db)
    await repo.ensure_builtin()
    return repo


def get_register_use_case(repo: UserRepository = Depends(get_user_repo)) -> RegisterUser:
    return RegisterUser(repo, BcryptPasswordHasher())


def get_auth_use_case(repo: UserRepository = Depends(get_user_repo)) -> AuthenticateUser:
    return AuthenticateUser(repo, BcryptPasswordHasher(), JwtTokenService())


def get_token_service() -> JwtTokenService:
    return JwtTokenService()


def _build_session_store() -> SessionStore:
    global _session_store, _redis_client
    if _session_store:
        return _session_store
    if settings.session_store_backend == "redis":
        _redis_client = Redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        _session_store = RedisRefreshSessionStore(_redis_client, prefix=settings.redis_session_prefix)
    else:
        _session_store = InMemoryRefreshSessionStore()
    return _session_store


def get_session_store() -> SessionStore:
    return _build_session_store()


def _set_cookie(
    response: Response,
    *,
    key: str,
    value: str,
    max_age: int | None = None,
    expires: datetime | None = None,
) -> None:
    response.set_cookie(
        key=key,
        value=value,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        domain=settings.cookie_domain,
        path=settings.cookie_path,
        max_age=max_age,
        expires=expires,
    )


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str, refresh_exp: datetime) -> None:
    _set_cookie(
        response,
        key=settings.access_cookie_name,
        value=access_token,
        max_age=settings.access_token_ttl_minutes * 60,
    )
    _set_cookie(
        response,
        key=settings.refresh_cookie_name,
        value=refresh_token,
        expires=refresh_exp,
    )
    if settings.enable_csrf_protection:
        response.set_cookie(
            key=CSRF_COOKIE_NAME,
            value=generate_csrf_token(),
            httponly=False,
            secure=settings.cookie_secure,
            samesite=settings.cookie_samesite,
            domain=settings.cookie_domain,
            path=settings.cookie_path,
        )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(settings.access_cookie_name, path=settings.cookie_path, domain=settings.cookie_domain)
    response.delete_cookie(settings.refresh_cookie_name, path=settings.cookie_path, domain=settings.cookie_domain)


async def register_session(result_user: User, refresh_jti: str, refresh_exp: datetime, store: RefreshSessionStore) -> None:
    if result_user.id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Kullanıcı kimliği eksik")
    await store.remember(jti=refresh_jti, user_id=result_user.id, expires_at=refresh_exp)


def _extract_access_token(request: Request) -> str | None:
    header = request.headers.get("Authorization")
    if header and header.lower().startswith("bearer "):
        return header.split(" ", 1)[1]
    cookie_value = request.cookies.get(settings.access_cookie_name)
    return cookie_value


async def get_current_user(
    request: Request,
    repo: UserRepository = Depends(get_user_repo),
) -> User:
    token = _extract_access_token(request)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Yetkilendirme gerekli")
    try:
        payload = decode_token(token)
    except TokenDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token geçersiz") from exc
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token türü geçersiz")
    user_id = payload.get("uid")
    user = await repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kullanıcı geçersiz")
    return user


def require_roles(*roles: str):
    async def dependency(user: User = Depends(get_current_user)) -> User:
        if roles and user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu işlem için yetkiniz yok")
        return user

    return dependency


@router.get("/csrf-token")
async def get_csrf_token(response: Response):
    if not settings.enable_csrf_protection:
        return {"csrf_token": None}
    token = generate_csrf_token()
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=token,
        httponly=False,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        domain=settings.cookie_domain,
        path=settings.cookie_path,
    )
    return {"csrf_token": token}


@router.post("/register", response_model=UserResponse, status_code=201)
async def register_user(payload: RegisterRequest, use_case: RegisterUser = Depends(get_register_use_case)):
    user = await use_case(email=payload.email, username=payload.username, password=payload.password)
    return UserResponse(id=user.id or 0, email=user.email, username=user.username, role=user.role)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    response: Response,
    payload: LoginRequest,
    use_case: AuthenticateUser = Depends(get_auth_use_case),
    session_store: RefreshSessionStore = Depends(get_session_store),
):
    if settings.enable_csrf_protection:
        validate_csrf(request)
    result = await use_case(email=payload.email, password=payload.password)
    await register_session(result.user, result.refresh_jti, result.refresh_expires_at, session_store)
    _set_auth_cookies(response, result.access_token, result.refresh_token, result.refresh_expires_at)
    return TokenResponse(access_token=result.access_token, refresh_token=result.refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    request: Request,
    response: Response,
    payload: RefreshTokenRequest | None = None,
    refresh_cookie: str | None = Cookie(default=None, alias=settings.refresh_cookie_name),
    session_store: RefreshSessionStore = Depends(get_session_store),
    repo: UserRepository = Depends(get_user_repo),
    token_service: JwtTokenService = Depends(get_token_service),
):
    if settings.enable_csrf_protection:
        validate_csrf(request)
    provided_token = payload.refresh_token if payload else None
    token_value = provided_token or refresh_cookie
    if not token_value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token gerekli")
    try:
        data = decode_token(token_value)
    except TokenDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token doğrulanamadı") from exc
    if data.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token türü geçersiz")
    jti = data.get("jti")
    if not jti or not await session_store.is_active(jti):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Oturum geçersiz veya süresi dolmuş")
    await session_store.revoke(jti)
    user_id = data.get("uid")
    user = await repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kullanıcı bulunamadı")

    access_token = token_service.create_access_token(subject=user.email, user_id=user.id or 0, role=user.role)
    refresh_payload = token_service.create_refresh_token(subject=user.email, user_id=user.id or 0)
    await session_store.remember(jti=refresh_payload.jti, user_id=user.id or 0, expires_at=refresh_payload.expires_at)
    _set_auth_cookies(response, access_token, refresh_payload.token, refresh_payload.expires_at)
    return TokenResponse(access_token=access_token, refresh_token=refresh_payload.token)


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    session_store: RefreshSessionStore = Depends(get_session_store),
    refresh_cookie: str | None = Cookie(default=None, alias=settings.refresh_cookie_name),
):
    if settings.enable_csrf_protection:
        validate_csrf(request)
    if refresh_cookie:
        try:
            payload = decode_token(refresh_cookie)
            jti = payload.get("jti")
            if jti:
                await session_store.revoke(jti)
        except TokenDecodeError:
            pass
    _clear_auth_cookies(response)
    return {"detail": "Oturum kapatıldı"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(require_roles("owner", "admin"))):
    return UserResponse(id=current_user.id or 0, email=current_user.email, username=current_user.username, role=current_user.role)


__all__ = ["router", "get_current_user", "require_roles", "get_user_repo", "get_role_repo"]

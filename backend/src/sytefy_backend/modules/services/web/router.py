"""Services HTTP routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from sytefy_backend.core.database import get_db
from sytefy_backend.modules.auth.domain.entities import User
from sytefy_backend.modules.auth.web.router import get_current_user, require_roles
from sytefy_backend.modules.services.application.interfaces import IServiceRepository
from sytefy_backend.modules.services.application.use_cases import CreateService, DeleteService, ListServices, UpdateService
from sytefy_backend.modules.services.infrastructure.repository import ServiceRepository
from sytefy_backend.modules.services.web.dto import ServiceCreateRequest, ServiceResponse, ServiceUpdateRequest

router = APIRouter(prefix="/services", tags=["Services"])


def get_repo(db: AsyncSession = Depends(get_db)) -> IServiceRepository:
    return ServiceRepository(db)


def get_create_use_case(repo: IServiceRepository = Depends(get_repo)) -> CreateService:
    return CreateService(repo)


def get_list_use_case(repo: IServiceRepository = Depends(get_repo)) -> ListServices:
    return ListServices(repo)


def get_update_use_case(repo: IServiceRepository = Depends(get_repo)) -> UpdateService:
    return UpdateService(repo)


def get_delete_use_case(repo: IServiceRepository = Depends(get_repo)) -> DeleteService:
    return DeleteService(repo)


def _to_response(service) -> ServiceResponse:
    return ServiceResponse(
        id=service.id or 0,
        name=service.name,
        description=service.description,
        price_amount=service.price_amount,
        price_currency=service.price_currency,
        duration_minutes=service.duration_minutes,
        status=service.status,
    )


@router.get("/", response_model=list[ServiceResponse])
async def list_services(
    current_user: User = Depends(get_current_user),
    use_case: ListServices = Depends(get_list_use_case),
    status_filter: str | None = None,
):
    services = await use_case(user_id=current_user.id or 0, status=status_filter)
    return [_to_response(service) for service in services]


@router.post("/", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(
    payload: ServiceCreateRequest,
    current_user: User = Depends(require_roles("owner", "admin")),
    use_case: CreateService = Depends(get_create_use_case),
):
    result = await use_case(
        user_id=current_user.id or 0,
        name=payload.name,
        description=payload.description,
        price_amount=payload.price_amount,
        price_currency=payload.price_currency,
        duration_minutes=payload.duration_minutes,
    )
    return _to_response(result.service)


@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: int,
    payload: ServiceUpdateRequest,
    current_user: User = Depends(require_roles("owner", "admin")),
    use_case: UpdateService = Depends(get_update_use_case),
):
    try:
        updated = await use_case(
            service_id=service_id,
            user_id=current_user.id or 0,
            name=payload.name,
            description=payload.description,
            price_amount=payload.price_amount,
            price_currency=payload.price_currency,
            duration_minutes=payload.duration_minutes,
            status=payload.status,
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Hizmet bulunamadı")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _to_response(updated)


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: int,
    current_user: User = Depends(require_roles("owner", "admin")),
    use_case: DeleteService = Depends(get_delete_use_case),
):
    await use_case(service_id=service_id, user_id=current_user.id or 0)
    return None

"""Customer routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from sytefy_backend.core.database import get_db
from sytefy_backend.modules.auth.web.router import get_current_user
from sytefy_backend.modules.auth.domain.entities import User
from sytefy_backend.modules.customers.application.use_cases import CreateCustomer, ListCustomers
from sytefy_backend.modules.customers.infrastructure.repository import CustomerRepository
from sytefy_backend.modules.customers.web.dto import CustomerCreateRequest, CustomerResponse

router = APIRouter(prefix="/customers", tags=["Customers"])


async def get_customer_repo(db: AsyncSession = Depends(get_db)) -> CustomerRepository:
    return CustomerRepository(db)


def get_list_use_case(repo: CustomerRepository = Depends(get_customer_repo)) -> ListCustomers:
    return ListCustomers(repo)


def get_create_use_case(repo: CustomerRepository = Depends(get_customer_repo)) -> CreateCustomer:
    return CreateCustomer(repo)


@router.get("/", response_model=list[CustomerResponse])
async def list_customers(
    current_user: User = Depends(get_current_user),
    use_case: ListCustomers = Depends(get_list_use_case),
):
    customers = await use_case(user_id=current_user.id or 0)
    return [
        CustomerResponse(
            id=customer.id or 0,
            name=customer.name,
            email=customer.email,
            phone=customer.phone,
            notes=customer.notes,
        )
        for customer in customers
    ]


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    payload: CustomerCreateRequest,
    current_user: User = Depends(get_current_user),
    use_case: CreateCustomer = Depends(get_create_use_case),
):
    if current_user.id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Kullanıcı kimliği eksik")
    customer = await use_case(
        user_id=current_user.id,
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        notes=payload.notes,
    )
    return CustomerResponse(
        id=customer.id or 0,
        name=customer.name,
        email=customer.email,
        phone=customer.phone,
        notes=customer.notes,
    )

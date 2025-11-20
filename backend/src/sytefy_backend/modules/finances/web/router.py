"""Invoice routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from sytefy_backend.core.database import get_db
from sytefy_backend.core.exceptions import ApplicationError
from sytefy_backend.modules.auth.domain.entities import User
from sytefy_backend.modules.auth.web.router import get_current_user, require_roles
from sytefy_backend.modules.finances.application.interfaces import IInvoiceRepository
from sytefy_backend.modules.finances.application.use_cases import CreateInvoice, DeleteInvoice, ListInvoices, UpdateInvoice
from sytefy_backend.modules.finances.infrastructure.repository import InvoiceRepository
from sytefy_backend.modules.finances.web.dto import InvoiceCreateRequest, InvoiceResponse, InvoiceUpdateRequest

router = APIRouter(prefix="/finances/invoices", tags=["Finances"])


def get_repo(db: AsyncSession = Depends(get_db)) -> IInvoiceRepository:
    return InvoiceRepository(db)


def to_response(invoice) -> InvoiceResponse:
    return InvoiceResponse(
        id=invoice.id or 0,
        number=invoice.number,
        title=invoice.title,
        description=invoice.description,
        amount=invoice.amount,
        currency=invoice.currency,
        status=invoice.status,
        due_date=invoice.due_date,
        issued_at=invoice.issued_at,
        customer_id=invoice.customer_id,
        created_at=invoice.created_at,
        updated_at=invoice.updated_at,
    )


@router.get("/", response_model=list[InvoiceResponse])
async def list_invoices(
    current_user: User = Depends(get_current_user),
    repo: IInvoiceRepository = Depends(get_repo),
    status_filter: str | None = None,
):
    use_case = ListInvoices(repo)
    try:
        invoices = await use_case(user_id=current_user.id or 0, status=status_filter)
    except ApplicationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return [to_response(inv) for inv in invoices]


@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    payload: InvoiceCreateRequest,
    current_user: User = Depends(require_roles("owner", "admin")),
    repo: IInvoiceRepository = Depends(get_repo),
):
    use_case = CreateInvoice(repo)
    try:
        result = await use_case(
            user_id=current_user.id or 0,
            title=payload.title,
            amount=payload.amount,
            currency=payload.currency,
            due_date=payload.due_date,
            customer_id=payload.customer_id,
            description=payload.description,
            number=payload.number,
            issued_at=payload.issued_at,
            status=payload.status,
        )
    except ApplicationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return to_response(result.invoice)


@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: int,
    payload: InvoiceUpdateRequest,
    current_user: User = Depends(require_roles("owner", "admin")),
    repo: IInvoiceRepository = Depends(get_repo),
):
    use_case = UpdateInvoice(repo)
    try:
        updated = await use_case(
            invoice_id=invoice_id,
            user_id=current_user.id or 0,
            title=payload.title,
            description=payload.description,
            amount=payload.amount,
            currency=payload.currency,
            due_date=payload.due_date,
            status=payload.status,
        )
    except ApplicationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return to_response(updated)


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    invoice_id: int,
    current_user: User = Depends(require_roles("owner", "admin")),
    repo: IInvoiceRepository = Depends(get_repo),
):
    use_case = DeleteInvoice(repo)
    try:
        await use_case(invoice_id=invoice_id, user_id=current_user.id or 0)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from starlette.requests import Request

from modules.organization.invoice.models.requests import (
    PaymentMethodRequest,
    SpendingLimitRequest,
)
from modules.organization.invoice.models.responses import (
    InvoiceResponse,
    PaymentMethodResponse,
    SpendingLimitResponse,
)
from modules.organization.invoice.service import InvoiceService
from modules.organization.invoice.webhook import InvoiceWebhook
from utils.auth import Authorize, VerifyToken

router = APIRouter(
    prefix="/organizations",
    responses={404: {"description": "Not found"}},
)

authorize = Authorize()
invoice_service = InvoiceService()
invoice_webhook = InvoiceWebhook()


@router.get("/{id}/invoices/pending")
def get_pending_invoice(id: str, token: str = Depends(HTTPBearer())) -> InvoiceResponse:
    user = authorize.user(VerifyToken(token.credentials).verify())
    authorize.is_self(user.organization_id, id)
    return invoice_service.get_pending_invoice(id)


@router.get("/{id}/invoices/payment-methods")
def get_payment_methods(
    id: str, token: str = Depends(HTTPBearer())
) -> list[PaymentMethodResponse]:
    user = authorize.user(VerifyToken(token.credentials).verify())
    authorize.is_self(user.organization_id, id)
    return invoice_service.get_payment_methods(id)


@router.post("/{id}/invoices/payment-methods")
def attach_payment_method(
    id: str,
    payment_method_request: PaymentMethodRequest,
    default: bool = True,
    token: str = Depends(HTTPBearer()),
) -> PaymentMethodResponse:
    user = authorize.user(VerifyToken(token.credentials).verify())
    authorize.is_self(user.organization_id, id)
    return invoice_service.attach_payment_method(id, payment_method_request, default)


@router.put("/{id}/invoices/payment-methods/default")
def set_default_payment_method(
    id: str,
    payment_method_request: PaymentMethodRequest,
    token: str = Depends(HTTPBearer()),
):
    user = authorize.user(VerifyToken(token.credentials).verify())
    authorize.is_self(user.organization_id, id)
    return invoice_service.set_default_payment_method(id, payment_method_request)


@router.delete("/{id}/invoices/payment-methods/{payment_method_id}")
def delete_payment_method(
    id: str,
    payment_method_id: str,
    token: str = Depends(HTTPBearer()),
) -> PaymentMethodResponse:
    user = authorize.user(VerifyToken(token.credentials).verify())
    authorize.is_self(user.organization_id, id)
    return invoice_service.detach_payment_method(id, payment_method_id)


@router.get("/{id}/invoices/limits")
def get_spending_limits(
    id: str, token: str = Depends(HTTPBearer())
) -> SpendingLimitResponse:
    user = authorize.user(VerifyToken(token.credentials).verify())
    authorize.is_self(user.organization_id, id)
    return invoice_service.get_spending_limits(id)


@router.put("/{id}/invoices/limits")
def update_spending_limit(
    id: str,
    spending_limit_request: SpendingLimitRequest,
    token: str = Depends(HTTPBearer()),
) -> SpendingLimitResponse:
    user = authorize.user(VerifyToken(token.credentials).verify())
    authorize.is_self(user.organization_id, id)
    return invoice_service.update_spending_limit(id, spending_limit_request)


@router.post("/invoices/webhook")
async def webhook(request: Request):
    return await invoice_webhook.handler(request)

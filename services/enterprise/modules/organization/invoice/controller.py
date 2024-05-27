from fastapi import APIRouter, Depends, Security, status
from starlette.requests import Request

from config import invoice_settings
from modules.organization.invoice.models.exceptions import StripeDisabledError
from modules.organization.invoice.models.requests import (
    CreditRequest,
    PaymentMethodRequest,
    SpendingLimitRequest,
)
from modules.organization.invoice.models.responses import (
    CreditResponse,
    InvoiceResponse,
    PaymentMethodResponse,
    SpendingLimitResponse,
)
from modules.organization.invoice.service import InvoiceService
from modules.organization.invoice.webhook import InvoiceWebhook
from utils.auth import Authorize, User, authenticate_user


def is_stripe_disabled(request: Request):
    if invoice_settings.stripe_disabled:
        raise StripeDisabledError()
    return request


router = APIRouter(
    prefix="/organizations",
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(is_stripe_disabled)],
)

authorize = Authorize()
invoice_service = InvoiceService()
invoice_webhook = InvoiceWebhook()


@router.get("/{id}/invoices/pending")
def get_pending_invoice(
    id: str, user: User = Security(authenticate_user)
) -> InvoiceResponse:
    authorize.is_self(user.organization_id, id)
    return invoice_service.get_pending_invoice(id)


@router.get("/{id}/invoices/payment-methods")
def get_payment_methods(
    id: str, user: User = Security(authenticate_user)
) -> list[PaymentMethodResponse]:
    authorize.is_self(user.organization_id, id)
    return invoice_service.get_payment_methods(id)


@router.post("/{id}/invoices/payment-methods", status_code=status.HTTP_201_CREATED)
def attach_payment_method(
    id: str,
    payment_method_request: PaymentMethodRequest,
    default: bool = True,
    user: User = Security(authenticate_user),
) -> PaymentMethodResponse:
    authorize.is_self(user.organization_id, id)
    return invoice_service.attach_payment_method(id, payment_method_request, default)


@router.put("/{id}/invoices/payment-methods/default")
def set_default_payment_method(
    id: str,
    payment_method_request: PaymentMethodRequest,
    user: User = Security(authenticate_user),
):
    authorize.is_self(user.organization_id, id)
    return invoice_service.set_default_payment_method(id, payment_method_request)


@router.delete("/{id}/invoices/payment-methods/{payment_method_id}")
def delete_payment_method(
    id: str, payment_method_id: str, user: User = Security(authenticate_user)
) -> PaymentMethodResponse:
    authorize.is_self(user.organization_id, id)
    return invoice_service.detach_payment_method(id, payment_method_id)


@router.get("/{id}/invoices/limits")
def get_spending_limits(
    id: str, user: User = Security(authenticate_user)
) -> SpendingLimitResponse:
    authorize.is_self(user.organization_id, id)
    return invoice_service.get_spending_limits(id)


@router.put("/{id}/invoices/limits")
def update_spending_limit(
    id: str,
    spending_limit_request: SpendingLimitRequest,
    user: User = Security(authenticate_user),
) -> SpendingLimitResponse:
    authorize.is_self(user.organization_id, id)
    return invoice_service.update_spending_limit(id, spending_limit_request)


@router.post("/{id}/invoices/credits", status_code=status.HTTP_201_CREATED)
def add_credits(
    id: str, credit_request: CreditRequest, user: User = Security(authenticate_user)
) -> CreditResponse:
    authorize.is_admin_user(user)
    return invoice_service.add_credits(id, user.id, credit_request)


@router.post("/invoices/webhook")
async def webhook(request: Request):
    return await invoice_webhook.handler(request)

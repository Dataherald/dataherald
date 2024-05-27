from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_402_PAYMENT_REQUIRED,
    HTTP_403_FORBIDDEN,
)

from exceptions.error_codes import BaseErrorCode, ErrorCodeData
from exceptions.exceptions import BaseError


class InvoiceErrorCode(BaseErrorCode):
    stripe_disabled = ErrorCodeData(
        status_code=HTTP_400_BAD_REQUEST, message="Stripe is disabled"
    )
    no_payment_method = ErrorCodeData(
        status_code=HTTP_402_PAYMENT_REQUIRED,
        message="No payment method on file",
    )
    last_payment_method = ErrorCodeData(
        status_code=HTTP_403_FORBIDDEN, message="Last payment method"
    )
    spending_limit_exceeded = ErrorCodeData(
        status_code=HTTP_403_FORBIDDEN, message="Spending limit exceeded"
    )
    hard_spending_limit_exceeded = ErrorCodeData(
        status_code=HTTP_403_FORBIDDEN,
        message="Hard spending limit exceeded",
    )
    subscription_past_due = ErrorCodeData(
        status_code=HTTP_402_PAYMENT_REQUIRED,
        message="Stripe subscription past due",
    )
    subscription_canceled = ErrorCodeData(
        status_code=HTTP_402_PAYMENT_REQUIRED,
        message="Stripe subscription canceled",
    )
    unknown_subscription_status = ErrorCodeData(
        status_code=HTTP_400_BAD_REQUEST,
        message="Unknown stripe subscription status",
    )
    is_enterprise_plan = ErrorCodeData(
        status_code=HTTP_400_BAD_REQUEST,
        message="Cannot perform action for enterprise plan",
    )
    cannot_update_spending_limit = ErrorCodeData(
        status_code=HTTP_400_BAD_REQUEST, message="Cannot update spending limit"
    )
    cannot_update_payment_method = ErrorCodeData(
        status_code=HTTP_400_BAD_REQUEST, message="Cannot update payment method"
    )
    missing_invoice_details = ErrorCodeData(
        status_code=HTTP_400_BAD_REQUEST,
        message="Organization missing invoice details",
    )


class InvoiceError(BaseError):
    """
    Base class for invoice exceptions
    """

    ERROR_CODES: BaseErrorCode = InvoiceErrorCode


class StripeDisabledError(InvoiceError):
    def __init__(self) -> None:
        super().__init__(error_code=InvoiceErrorCode.stripe_disabled.name)


class NoPaymentMethodError(InvoiceError):
    def __init__(self, organization_id: str) -> None:
        super().__init__(
            error_code=InvoiceErrorCode.no_payment_method.name,
            detail={"organization_id": organization_id},
        )


class LastPaymentMethodError(InvoiceError):
    def __init__(self, organization_id: str) -> None:
        super().__init__(
            error_code=InvoiceErrorCode.last_payment_method.name,
            detail={"organization_id": organization_id},
        )


class SpendingLimitExceededError(InvoiceError):
    def __init__(self, organization_id: str) -> None:
        super().__init__(
            error_code=InvoiceErrorCode.spending_limit_exceeded.name,
            detail={"organization_id": organization_id},
        )


class HardSpendingLimitExceededError(InvoiceError):
    def __init__(self, organization_id: str) -> None:
        super().__init__(
            error_code=InvoiceErrorCode.hard_spending_limit_exceeded.name,
            detail={"organization_id": organization_id},
        )


class SubscriptionPastDueError(InvoiceError):
    def __init__(self, organization_id: str) -> None:
        super().__init__(
            error_code=InvoiceErrorCode.subscription_past_due.name,
            detail={"organization_id": organization_id},
        )


class SubscriptionCanceledError(InvoiceError):
    def __init__(self, organization_id: str) -> None:
        super().__init__(
            error_code=InvoiceErrorCode.subscription_canceled.name,
            detail={"organization_id": organization_id},
        )


class UnknownSubscriptionStatusError(InvoiceError):
    def __init__(self, organization_id: str) -> None:
        super().__init__(
            error_code=InvoiceErrorCode.unknown_subscription_status.name,
            detail={"organization_id": organization_id},
        )


class IsEnterprisePlanError(InvoiceError):
    def __init__(self, organization_id: str) -> None:
        super().__init__(
            error_code=InvoiceErrorCode.is_enterprise_plan.name,
            detail={"organization_id": organization_id},
        )


class CannotUpdateSpendingLimitError(InvoiceError):
    def __init__(self, organization_id: str) -> None:
        super().__init__(
            error_code=InvoiceErrorCode.cannot_update_spending_limit.name,
            detail={"organization_id": organization_id},
        )


class CannotUpdatePaymentMethodError(InvoiceError):
    def __init__(self, organization_id: str) -> None:
        super().__init__(
            error_code=InvoiceErrorCode.cannot_update_payment_method.name,
            detail={"organization_id": organization_id},
        )


class MissingInvoiceDetailsError(InvoiceError):
    def __init__(self, organization_id: str) -> None:
        super().__init__(
            error_code=InvoiceErrorCode.missing_invoice_details.name,
            detail={"organization_id": organization_id},
        )

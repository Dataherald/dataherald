from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_402_PAYMENT_REQUIRED,
)

from exceptions.error_codes import BaseErrorCode, ErrorCodeData


class InvoiceErrorCode(BaseErrorCode):
    no_payment_method = ErrorCodeData(
        status_code=HTTP_402_PAYMENT_REQUIRED,
        message="No payment method on file",
    )
    last_payment_method = ErrorCodeData(
        status_code=HTTP_400_BAD_REQUEST, message="Last payment method"
    )
    spending_limit_exceeded = ErrorCodeData(
        status_code=HTTP_402_PAYMENT_REQUIRED, message="Spending limit exceeded"
    )
    hard_spending_limit_exceeded = ErrorCodeData(
        status_code=HTTP_402_PAYMENT_REQUIRED,
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

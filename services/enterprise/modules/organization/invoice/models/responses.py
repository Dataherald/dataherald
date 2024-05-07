from datetime import datetime

from pydantic import BaseModel

from modules.organization.invoice.models.entities import Credit, UsageInvoice


class InvoiceResponse(UsageInvoice):
    available_credits: int = 0
    total_credits: int = 0
    amount_due: int = 0
    spending_limit: int | None
    current_period_start: datetime | None
    current_period_end: datetime | None


class PaymentMethodResponse(BaseModel):
    id: str
    funding: str
    brand: str
    last4: str
    exp_month: int
    exp_year: int
    is_default: bool


class SpendingLimitResponse(BaseModel):
    spending_limit: int
    hard_spending_limit: int


class CreditResponse(Credit):
    pass

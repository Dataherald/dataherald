from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class UsageType(str, Enum):
    SQL_GENERATION = "SQL_GENERATION"
    FINETUNING_GPT_35 = "FINETUNING_GPT_35"
    FINETUNING_GPT_4 = "FINETUNING_GPT_4"


class BaseUsage(BaseModel):
    type: UsageType
    quantity: int = 0
    description: str | None


class RecordStatus(str, Enum):
    UNRECORDED = "UNRECORDED"
    RECORDED = "RECORDED"


class Usage(BaseUsage):
    id: str | None
    organization_id: str
    status: RecordStatus
    created_at: datetime = datetime.now()


class Credit(BaseModel):
    id: str | None
    organization_id: str
    status: RecordStatus
    amount: int = 0
    description: str | None
    created_at: datetime = datetime.now()


class PaymentPlan(str, Enum):
    CREDIT_ONLY = "CREDIT_ONLY"
    USAGE_BASED = "USAGE_BASED"
    ENTERPRISE = "ENTERPRISE"


class InvoiceDetails(BaseModel):
    plan: PaymentPlan
    billing_cycle_anchor: int | None
    spending_limit: int | None  # in cents
    hard_spending_limit: int | None  # in cents
    available_credits: int | None  # in cents
    stripe_customer_id: str | None
    stripe_subscription_id: str | None
    stripe_subscription_status: str | None


class UsageInvoice(BaseModel):
    sql_generation_cost: int = 0
    finetuning_gpt_35_cost: int = 0
    finetuning_gpt_4_cost: int = 0

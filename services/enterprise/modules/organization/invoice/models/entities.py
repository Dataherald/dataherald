from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from utils.validation import ObjectIdString


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
    id: ObjectIdString | None
    organization_id: ObjectIdString
    status: RecordStatus
    created_at: datetime = datetime.now()


class Credit(BaseModel):
    id: ObjectIdString | None
    organization_id: ObjectIdString
    status: RecordStatus
    amount: int = 0
    description: str | None
    created_at: datetime = datetime.now()


class PaymentPlan(str, Enum):
    CREDIT_ONLY = "CREDIT_ONLY"
    USAGE_BASED = "USAGE_BASED"
    ENTERPRISE = "ENTERPRISE"


class StripeSubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    UNPAID = "unpaid"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    TRIALING = "trialing"
    PAST_DUE = "past_due"


class InvoiceDetails(BaseModel):
    plan: PaymentPlan
    billing_cycle_anchor: int | None
    spending_limit: int | None  # in cents
    hard_spending_limit: int | None  # in cents
    available_credits: int | None  # in cents
    stripe_customer_id: str | None
    stripe_subscription_id: str | None
    stripe_subscription_status: StripeSubscriptionStatus | None


class UsageInvoice(BaseModel):
    sql_generation_cost: int = 0
    finetuning_gpt_35_cost: int = 0
    finetuning_gpt_4_cost: int = 0


class MockStripeCustomer(BaseModel):
    id: str | None = None
    name: str | None = None


class MockStripeSubscription(BaseModel):
    id: str | None = None
    status: str | None = None
    billing_cycle_anchor: int | None = None

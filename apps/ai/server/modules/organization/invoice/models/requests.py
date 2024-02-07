from pydantic import BaseModel


class SpendingLimitRequest(BaseModel):
    spending_limit: float


class PaymentMethodRequest(BaseModel):
    payment_method_id: str

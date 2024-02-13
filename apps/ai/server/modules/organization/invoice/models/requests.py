from pydantic import BaseModel, conint


class SpendingLimitRequest(BaseModel):
    spending_limit: float


class PaymentMethodRequest(BaseModel):
    payment_method_id: str


class CreditRequest(BaseModel):
    amount: conint(gt=0)
    description: str

import calendar
import uuid
from datetime import date, datetime, timedelta, timezone

import stripe

from config import invoice_settings


class Billing:
    def __init__(self):
        stripe.api_key = invoice_settings.stripe_api_key
        stripe.max_network_retries = 2

    def get_upcoming_invoice(self, customer_id: str) -> stripe.Invoice:
        return stripe.Invoice.upcoming(customer=customer_id)

    def get_subscription(self, subscription_id: str) -> stripe.Subscription:
        return stripe.Subscription.retrieve(subscription_id)

    def get_current_subscription_period(
        self, subscription_id: str
    ) -> tuple[datetime, datetime]:
        subscription = stripe.Subscription.retrieve(subscription_id)
        return (
            datetime.fromtimestamp(subscription.current_period_start),
            datetime.fromtimestamp(subscription.current_period_end),
        )

    def get_current_subscription_period_with_anchor(
        self, billing_cycle_anchor: int
    ) -> tuple[datetime, datetime]:
        today = date.today()
        anchor_day = datetime.fromtimestamp(billing_cycle_anchor).day

        # Calculate the last date of the current month
        _, last_day_current_month = calendar.monthrange(today.year, today.month)
        last_date_current_month = datetime(
            today.year, today.month, last_day_current_month
        )

        # Calculate the last date of the last month
        first_day_last_month = today.replace(day=1) - timedelta(days=1)
        _, last_day_last_month = calendar.monthrange(
            first_day_last_month.year, first_day_last_month.month
        )
        last_date_last_month = datetime(
            first_day_last_month.year, first_day_last_month.month, last_day_last_month
        )
        # Calculate the last date of the next month
        first_day_next_month = today.replace(day=1) + timedelta(days=32)
        _, last_day_next_month = calendar.monthrange(
            first_day_next_month.year, first_day_next_month.month
        )
        last_date_next_month = datetime(
            first_day_next_month.year, first_day_next_month.month, last_day_next_month
        )

        if today.day < anchor_day:
            start_date = datetime(
                last_date_last_month.year,
                last_date_last_month.month,
                min(anchor_day, last_date_last_month.day),
                tzinfo=timezone.utc,
            )
            end_date = datetime(
                today.year,
                today.month,
                min(anchor_day, last_date_current_month.day),
                tzinfo=timezone.utc,
            )

        else:
            start_date = datetime(
                today.year,
                today.month,
                min(anchor_day, last_date_current_month.day),
                tzinfo=timezone.utc,
            )
            end_date = datetime(
                last_date_next_month.year,
                last_date_next_month.month,
                min(anchor_day, last_date_next_month.day),
                tzinfo=timezone.utc,
            )
        return (start_date, end_date)

    def create_subscription(self, customer_id: str) -> stripe.Subscription:
        return stripe.Subscription.create(
            customer=customer_id,
            items=[
                {"price": invoice_settings.sql_generation_price_id},
                {"price": invoice_settings.finetuning_gpt_35_price_id},
                {"price": invoice_settings.finetuning_gpt_4_price_id},
            ],
            idempotency_key=str(uuid.uuid4()),
        )

    def construct_event(self, payload: bytes, sig_header: str):
        return stripe.Webhook.construct_event(
            payload, sig_header, invoice_settings.stripe_webhook_secret
        )

    def get_customer(self, customer_id: str) -> stripe.Customer:
        return stripe.Customer.retrieve(customer_id)

    def create_customer(self, name: str) -> stripe.Customer:
        return stripe.Customer.create(name=name, idempotency_key=str(uuid.uuid4()))

    def get_payment_methods(self, customer_id: str) -> list[stripe.PaymentMethod]:
        return stripe.Customer.list_payment_methods(customer_id)

    def get_payment_method(self, payment_method_id: str) -> stripe.PaymentMethod:
        return stripe.PaymentMethod.retrieve(payment_method_id)

    def attach_payment_method(
        self, customer_id: str, payment_method_id: str
    ) -> stripe.PaymentMethod:
        return stripe.PaymentMethod.attach(
            payment_method_id,
            customer=customer_id,
            idempotency_key=str(uuid.uuid4()),
        )

    def set_default_payment_method(
        self, customer_id: str, payment_method_id: str
    ) -> stripe.Customer:
        return stripe.Customer.modify(
            customer_id,
            invoice_settings={"default_payment_method": payment_method_id},
            idempotency_key=str(uuid.uuid4()),
        )

    def detach_payment_method(self, payment_method_id: str) -> stripe.PaymentMethod:
        return stripe.PaymentMethod.detach(
            payment_method_id, idempotency_key=str(uuid.uuid4())
        )

    def pay_past_due_subscription_invoices(self, customer_id: str) -> bool:
        try:
            subscriptions = stripe.Subscription.list(
                customer=customer_id,
                status="past_due",
                limit=10,
            )
            if subscriptions.data:
                for subscription in subscriptions:
                    invoices = stripe.Invoice.list(
                        subscription=subscription.id,
                        status="open",
                        limit=10,
                    )
                    if invoices.data:
                        for invoice in invoices:
                            print(f"paying past due invoice: {invoice.id}")
                            stripe.Invoice.pay(
                                invoice.id, idempotency_key=str(uuid.uuid4())
                            )
        except Exception as e:
            print(f"failed to pay past due subscription invoices: {e}")
            return False

        return True

    def create_balance_transaction(
        self, customer_id: str, amount: int, description: str
    ) -> stripe.BalanceTransaction:
        return stripe.Customer.create_balance_transaction(
            customer_id,
            amount=amount,
            currency="usd",
            description=description,
        )

from datetime import datetime

from stripe import PaymentMethod

from config import invoice_settings
from modules.organization.invoice.models.entities import (
    Credit,
    PaymentPlan,
    RecordStatus,
    StripeSubscriptionStatus,
    Usage,
    UsageInvoice,
    UsageType,
)
from modules.organization.invoice.models.exceptions import (
    CannotUpdatePaymentMethodError,
    CannotUpdateSpendingLimitError,
    HardSpendingLimitExceededError,
    IsEnterprisePlanError,
    LastPaymentMethodError,
    MissingInvoiceDetailsError,
    NoPaymentMethodError,
    SpendingLimitExceededError,
    SubscriptionCanceledError,
    SubscriptionPastDueError,
    UnknownSubscriptionStatusError,
)
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
from modules.organization.invoice.repository import InvoiceRepository
from modules.organization.repository import OrganizationRepository
from utils.analytics import Analytics, EventName, EventType
from utils.billing import Billing


class InvoiceService:
    def __init__(self):
        self.billing = Billing()
        self.repo = InvoiceRepository()
        self.org_repo = OrganizationRepository()
        self.analytics = Analytics()
        self.cost_dict = {
            UsageType.SQL_GENERATION: invoice_settings.sql_generation_cost,
            UsageType.FINETUNING_GPT_35: invoice_settings.finetuning_gpt_35_cost,
            UsageType.FINETUNING_GPT_4: invoice_settings.finetuning_gpt_4_cost,
        }

    def get_spending_limits(self, org_id: str) -> SpendingLimitResponse:
        organization = self.org_repo.get_organization(org_id)
        return SpendingLimitResponse(
            spending_limit=organization.invoice_details.spending_limit,
            hard_spending_limit=organization.invoice_details.hard_spending_limit,
        )

    def update_spending_limit(
        self, org_id: str, spending_limit_request: SpendingLimitRequest
    ) -> SpendingLimitResponse:
        organization = self.org_repo.get_organization(org_id)
        if (
            spending_limit_request.spending_limit >= 0
            and spending_limit_request.spending_limit
            <= organization.invoice_details.hard_spending_limit
            and (
                self.repo.update_spending_limit(
                    org_id, spending_limit_request.spending_limit
                )
                == 1
            )
        ):
            return SpendingLimitResponse(
                spending_limit=spending_limit_request.spending_limit,
                hard_spending_limit=organization.invoice_details.hard_spending_limit,
            )

        raise CannotUpdateSpendingLimitError(org_id)

    def get_pending_invoice(self, org_id: str) -> InvoiceResponse:
        organization = self.org_repo.get_organization(org_id)
        (
            current_period_start,
            current_period_end,
        ) = self.billing.get_current_subscription_period_with_anchor(
            organization.invoice_details.billing_cycle_anchor
        )
        upcoming_invoice = self.billing.get_upcoming_invoice(
            organization.invoice_details.stripe_customer_id
        )
        usage_invoice = UsageInvoice()
        for item in upcoming_invoice.lines:
            cost = item.quantity * item.price.unit_amount
            if item.price.lookup_key == UsageType.SQL_GENERATION:
                usage_invoice.sql_generation_cost = cost
            elif item.price.lookup_key == UsageType.FINETUNING_GPT_35:
                usage_invoice.finetuning_gpt_35_cost = cost
            elif item.price.lookup_key == UsageType.FINETUNING_GPT_4:
                usage_invoice.finetuning_gpt_4_cost = cost

        unrecorded_usage_invoice = self._get_invoice_from_usages(
            self.repo.get_usages(
                org_id,
                datetime.fromtimestamp(
                    organization.invoice_details.billing_cycle_anchor
                ),
                datetime.now(),
                record_status=RecordStatus.UNRECORDED,
            )
        )

        usage_invoice.sql_generation_cost += (
            unrecorded_usage_invoice.sql_generation_cost
        )
        usage_invoice.finetuning_gpt_35_cost += (
            unrecorded_usage_invoice.finetuning_gpt_35_cost
        )
        usage_invoice.finetuning_gpt_4_cost += (
            unrecorded_usage_invoice.finetuning_gpt_4_cost
        )

        unrecorded_usage_cost = self._calculate_total_usage_cost(
            unrecorded_usage_invoice
        )
        unrecorded_credits = self._calculate_total_credits(
            self.repo.get_credits(org_id, RecordStatus.UNRECORDED)
        )
        return InvoiceResponse(
            **usage_invoice.dict(),
            available_credits=organization.invoice_details.available_credits,
            total_credits=sum(
                credit.amount for credit in self.repo.get_positive_credits(org_id)
            ),
            amount_due=upcoming_invoice.amount_due  # recorded usage - recorded credits
            + unrecorded_usage_cost
            + unrecorded_credits,
            spending_limit=organization.invoice_details.spending_limit,
            current_period_start=current_period_start,
            current_period_end=current_period_end,
        )

    def get_payment_methods(self, org_id: str) -> list[PaymentMethodResponse]:
        organization = self.org_repo.get_organization(org_id)

        customer = self.billing.get_customer(
            organization.invoice_details.stripe_customer_id
        )
        payment_methods = self.billing.get_payment_methods(
            organization.invoice_details.stripe_customer_id
        )
        return [
            self._get_mapped_payment_method_response(
                payment_method,
                payment_method.id
                in {
                    customer.invoice_settings.default_payment_method,
                    customer.default_source,
                },
            )
            for payment_method in payment_methods
        ]

    def attach_payment_method(
        self,
        org_id: str,
        payment_method_request: PaymentMethodRequest,
        is_default: bool,
    ) -> PaymentMethodResponse:
        organization = self.org_repo.get_organization(org_id)
        payment_method = self.billing.attach_payment_method(
            organization.invoice_details.stripe_customer_id,
            payment_method_request.payment_method_id,
        )
        if is_default:
            self.billing.set_default_payment_method(
                organization.invoice_details.stripe_customer_id,
                payment_method_request.payment_method_id,
            )
            self.repo.update_payment_plan(org_id, PaymentPlan.USAGE_BASED)
        return self._get_mapped_payment_method_response(payment_method, is_default)

    def set_default_payment_method(
        self,
        org_id: str,
        payment_method_request: PaymentMethodRequest,
    ):
        organization = self.org_repo.get_organization(org_id)
        customer = self.billing.set_default_payment_method(
            organization.invoice_details.stripe_customer_id,
            payment_method_request.payment_method_id,
        )

        if (
            customer.invoice_settings.default_payment_method
            == payment_method_request.payment_method_id
        ):
            return {"success": True}

        raise CannotUpdatePaymentMethodError(org_id)

    def detach_payment_method(
        self, org_id: str, payment_method_id: str
    ) -> PaymentMethodResponse:
        organization = self.org_repo.get_organization(org_id)
        customer = self.billing.get_customer(
            organization.invoice_details.stripe_customer_id
        )
        payment_methods = self.billing.get_payment_methods(
            organization.invoice_details.stripe_customer_id
        )
        if len(payment_methods) <= 1:
            raise LastPaymentMethodError(org_id)

        # check if payment method exists for customer, avoids using stripe api
        payment_method = None
        for pm in payment_methods:
            if pm.id == payment_method_id:
                payment_method = pm
                break

        if payment_method:
            payment_method = self.billing.detach_payment_method(payment_method.id)
            if customer.invoice_settings.default_payment_method == payment_method.id:
                for pm in payment_methods:
                    if pm.id != payment_method.id:
                        self.billing.set_default_payment_method(
                            organization.invoice_details.stripe_customer_id, pm.id
                        )
                        break
            return self._get_mapped_payment_method_response(payment_method, False)

        raise NoPaymentMethodError(org_id)

    def record_usage(
        self,
        org_id: str,
        type: UsageType,
        quantity: int = 0,
        description: str = None,
    ):
        if invoice_settings.stripe_disabled:
            return
        organization = self.org_repo.get_organization(org_id)
        if organization.invoice_details.plan == PaymentPlan.ENTERPRISE:
            return

        usage = Usage(
            type=type,
            quantity=quantity,
            organization_id=org_id,
            created_at=datetime.now(),
            description=description,
            status=RecordStatus.UNRECORDED,
        )
        usage_id = self.repo.create_usage(usage)
        print(f"New usage created: {usage_id}")
        available_credits = organization.invoice_details.available_credits
        self._apply_unrecorded_credits(
            org_id,
            available_credits,
            self.cost_dict[type] * quantity,
            f"negative credit from usage {usage_id}",
        )

        self.analytics.track(
            org_id,
            EventName.usage_recorded,
            EventType.usage_event(
                id=usage_id,
                organization_id=org_id,
                type=type,
                cost=round(self.cost_dict[type] * quantity / 100, 2),
            ),
        )

    def check_usage(
        self,
        org_id: str,
        type: UsageType,
        quantity: int = 0,
    ):
        if invoice_settings.stripe_disabled:
            return
        organization = self.org_repo.get_organization(org_id)
        if not organization.invoice_details:
            raise MissingInvoiceDetailsError(org_id)
        # skip check if enterprise
        if organization.invoice_details.plan != PaymentPlan.ENTERPRISE:
            if (
                organization.invoice_details.stripe_subscription_status
                != StripeSubscriptionStatus.ACTIVE
            ):
                if (
                    organization.invoice_details.stripe_subscription_status
                    == StripeSubscriptionStatus.PAST_DUE
                ):
                    raise SubscriptionPastDueError(org_id)
                if (
                    organization.invoice_details.stripe_subscription_status
                    == StripeSubscriptionStatus.CANCELED
                ):
                    raise SubscriptionCanceledError(org_id)
                raise UnknownSubscriptionStatusError(org_id)
            (
                start_date,
                end_date,
            ) = self.billing.get_current_subscription_period_with_anchor(
                organization.invoice_details.billing_cycle_anchor
            )
            usages = self.repo.get_usages(org_id, start_date, end_date)
            usage = Usage(
                type=type,
                quantity=quantity,
                status=RecordStatus.UNRECORDED,
                organization_id=org_id,
            )
            usages.append(usage)
            # for usage based and credit only
            total_usage_cost = self._calculate_total_usage_cost(
                self._get_invoice_from_usages(usages)
            )
            if total_usage_cost > organization.invoice_details.hard_spending_limit:
                raise HardSpendingLimitExceededError(org_id)
            if total_usage_cost > organization.invoice_details.spending_limit:
                raise SpendingLimitExceededError(org_id)

            # check for available credits if credit only
            if organization.invoice_details.plan == PaymentPlan.CREDIT_ONLY:
                if (
                    self._calculate_total_usage_cost(
                        self._get_invoice_from_usages([usage])
                    )
                    > organization.invoice_details.available_credits
                ):
                    raise NoPaymentMethodError(org_id)

    def add_credits(
        self, org_id: str, user_id: str, credit_request: CreditRequest
    ) -> CreditResponse:
        organization = self.org_repo.get_organization(org_id)
        if organization.invoice_details.plan == PaymentPlan.ENTERPRISE:
            raise IsEnterprisePlanError(org_id)

        credit_id = self.repo.create_credit(
            Credit(
                organization_id=org_id,
                amount=credit_request.amount,
                status=RecordStatus.RECORDED,
                description=f"added by {user_id}: {credit_request.description}",
            )
        )
        print(f"New credit created: {credit_id}")
        # apply credits to recorded usage
        recorded_amount_due = self.billing.get_upcoming_invoice(
            organization.invoice_details.stripe_customer_id
        ).amount_due
        credits_due = min(max(recorded_amount_due, 0), credit_request.amount)
        if credits_due > 0:
            self.repo.create_credit(
                Credit(
                    organization_id=org_id,
                    amount=-credits_due,
                    status=RecordStatus.RECORDED,
                    description=f"negative credits for stripe pending invoice; used from new credit {credit_id}",
                )
            )
            self.billing.create_balance_transaction(
                organization.invoice_details.stripe_customer_id,
                -credits_due,
                "add credit balance",
            )
        # apply credits to unrecorded usage
        new_amount_due = self.get_pending_invoice(org_id).amount_due
        available_credits = (
            organization.invoice_details.available_credits
            + credit_request.amount
            - credits_due
        )
        self._apply_unrecorded_credits(
            org_id,
            available_credits,
            new_amount_due,
            f"negative credits for pending invoice; used from new credit {credit_id}",
        )
        return self.repo.get_credit(credit_id)

    def _get_invoice_from_usages(self, usages: list[Usage]) -> UsageInvoice:
        usage_invoice = {
            UsageType.SQL_GENERATION: 0,
            UsageType.FINETUNING_GPT_35: 0,
            UsageType.FINETUNING_GPT_4: 0,
        }
        for usage in usages:
            usage_invoice[usage.type] += usage.quantity * self.cost_dict[usage.type]

        return UsageInvoice(
            sql_generation_cost=usage_invoice[UsageType.SQL_GENERATION],
            finetuning_gpt_35_cost=usage_invoice[UsageType.FINETUNING_GPT_35],
            finetuning_gpt_4_cost=usage_invoice[UsageType.FINETUNING_GPT_4],
        )

    def _calculate_total_usage_cost(self, usage_invoice: UsageInvoice) -> int:
        return (
            usage_invoice.sql_generation_cost
            + usage_invoice.finetuning_gpt_35_cost
            + usage_invoice.finetuning_gpt_4_cost
        )

    def _calculate_total_credits(self, credits: list[Credit]) -> int:
        return sum([credit.amount for credit in credits])

    def _get_mapped_payment_method_response(
        self, payment_method: PaymentMethod, is_defualt: bool
    ) -> PaymentMethodResponse:
        return PaymentMethodResponse(
            id=payment_method.id,
            funding=payment_method.type,
            brand=payment_method.card.brand,
            last4=payment_method.card.last4,
            exp_month=payment_method.card.exp_month,
            exp_year=payment_method.card.exp_year,
            is_default=is_defualt,
        )

    def _apply_unrecorded_credits(
        self,
        org_id: str,
        available_credits: int,
        amount_due: int,
        description: str = None,
    ):
        credits_due = 0
        if available_credits > 0 and amount_due > 0:
            credits_due = min(available_credits, amount_due)
            neg_credit_id = self.repo.create_credit(
                Credit(
                    organization_id=org_id,
                    amount=-credits_due,
                    status=RecordStatus.UNRECORDED,
                    description=description,
                )
            )
            print(f"New negative credit created: {neg_credit_id}")
        self.repo.update_available_credits(org_id, available_credits - credits_due)

import stripe
from starlette.requests import Request

from modules.organization.invoice.models.entities import PaymentPlan
from modules.organization.invoice.repository import InvoiceRepository
from modules.organization.repository import OrganizationRepository
from utils.billing import Billing


class InvoiceWebhook:
    def __init__(self):
        self.billing = Billing()
        self.repo = InvoiceRepository()
        self.org_repo = OrganizationRepository()
        self.event_type_handlers = {
            "invoice.payment_failed": self.handle_payment_failed_event,
            "customer.subscription.updated": self.handle_subscription_updated_event,
            "customer.subscription.deleted": self.handle_subscription_deleted_event,
            "customer.updated": self.handle_customer_updated_event,
            "payment_method.detached": self.handle_payment_method_detached_event,
        }

    # When payment fails, update plan to credit only
    def handle_payment_failed_event(self, event: stripe.Event):
        customer_id = event.data.object["customer"]
        organization = self.org_repo.get_organization_by_customer_id(customer_id)
        if organization:
            print("Payment failed, update plan to credit only")
            self.repo.update_payment_plan(organization.id, PaymentPlan.CREDIT_ONLY)

    # When billing cycle anchor is updated, update it in the database
    def handle_subscription_updated_event(self, event: stripe.Event):
        customer_id = event.data.object["customer"]
        subscription_id = event.data.object["id"]
        previous_attributes = event.data.previous_attributes
        organization = self.org_repo.get_organization_by_customer_id(customer_id)
        if (
            organization
            and organization.invoice_details.stripe_subscription_id == subscription_id
        ):
            subscription_status = event.data.object["status"]
            print(
                f"Subscription updated with status {subscription_status} in organization: {organization.id}"
            )
            self.repo.update_stripe_subcription_status(
                organization.id, subscription_status
            )
            if previous_attributes and "billing_cycle_anchor" in previous_attributes:
                print(
                    f"Billing cycle anchor updated in organization: {organization.id}"
                )
                self.repo.update_billing_cyce_anchor(
                    organization.id, event.data.object["billing_cycle_anchor"]
                )

    def handle_subscription_deleted_event(self, event: stripe.Event):
        customer_id = event.data.object["customer"]
        subscription_id = event.data.object["id"]
        organization = self.org_repo.get_organization_by_customer_id(customer_id)
        if (
            organization
            and organization.invoice_details.stripe_subscription_id == subscription_id
        ):
            subscription_status = event.data.object["status"]
            print(
                f"Subscription updated with status {subscription_status} in organization: {organization.id}"
            )
            self.repo.update_stripe_subcription_status(
                organization.id, subscription_status
            )

    # When customer is updated, check if default payment method changes
    # Charge past due invoices and charge it to the default payment method
    def handle_customer_updated_event(self, event: stripe.Event):
        customer_id = event.data.object["id"]
        previous_attributes = event.data.previous_attributes
        organization = self.org_repo.get_organization_by_customer_id(customer_id)
        if organization and previous_attributes:
            if "default_source" in previous_attributes or previous_attributes.get(
                "invoice_settings", {}
            ).get("default_payment_method"):
                # if default payment method is added, change plan to usage based
                self.repo.update_payment_plan(organization.id, PaymentPlan.USAGE_BASED)
                # if payment intent fails, event is triggered and plan is updated back to credit only
                if not self.billing.pay_past_due_subscription_invoices(customer_id):
                    # if payment logic fails, update plan to credit only
                    self.repo.update_payment_plan(
                        organization.id, PaymentPlan.CREDIT_ONLY
                    )

    # When payment method is detached, check if there are no more payment methods, if so, update plan to credit only
    def handle_payment_method_detached_event(self, event: stripe.Event):
        customer_id = event.data.previous_attributes.get("customer")
        if customer_id:
            organization = self.org_repo.get_organization_by_customer_id(customer_id)
            if organization and len(self.billing.get_payment_methods(customer_id)) < 1:
                print("No payment methods left, update plan to credit only")
                self.repo.update_payment_plan(organization.id, PaymentPlan.CREDIT_ONLY)
        else:
            print("customer id not found in payment method detached event")

    async def handler(self, request: Request):
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        try:
            event = self.billing.construct_event(payload, sig_header)
        except ValueError as e:
            # Invalid payload
            raise e
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            raise e
        event_type = event.type
        if event_type in self.event_type_handlers:
            self.event_type_handlers[event_type](event)
        else:
            print(f"Unhandled event type: {event_type}")

        return {"status": "success"}

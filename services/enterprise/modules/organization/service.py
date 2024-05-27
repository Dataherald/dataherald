import openai

from config import invoice_settings
from modules.organization.invoice.models.entities import (
    Credit,
    InvoiceDetails,
    MockStripeCustomer,
    MockStripeSubscription,
    PaymentPlan,
    RecordStatus,
)
from modules.organization.invoice.repository import InvoiceRepository
from modules.organization.models.entities import (
    Organization,
    SlackConfig,
    SlackInstallation,
)
from modules.organization.models.exceptions import (
    CannotCreateOrganizationError,
    CannotDeleteOrganizationError,
    CannotUpdateOrganizationError,
    InvalidLlmApiKeyError,
    OrganizationNotFoundError,
    SlackInstallationNotFoundError,
)
from modules.organization.models.requests import OrganizationRequest
from modules.organization.models.responses import OrganizationResponse
from modules.organization.repository import OrganizationRepository
from utils.analytics import Analytics, EventName, EventType
from utils.billing import Billing
from utils.encrypt import FernetEncrypt


class OrganizationService:
    def __init__(self):
        self.repo = OrganizationRepository()
        self.invoice_repo = InvoiceRepository()
        self.billing = Billing()
        self.analytics = Analytics()

    def get_organizations(self) -> list[OrganizationResponse]:
        return self.repo.get_organizations()

    def get_organization(self, org_id: str) -> OrganizationResponse:
        return self.repo.get_organization(org_id)

    def get_organization_by_slack_workspace_id(
        self, slack_workspace_id: str
    ) -> OrganizationResponse:
        organization = self.repo.get_organization_by_slack_workspace_id(
            slack_workspace_id
        )
        if organization:
            return organization
        raise OrganizationNotFoundError(slack_workspace_id=slack_workspace_id)

    def add_organization(
        self, org_request: OrganizationRequest
    ) -> OrganizationResponse:
        if org_request.llm_api_key:
            self._validate_api_key(org_request.llm_api_key)
            org_request.llm_api_key = self._encrypt_llm_credentials(
                org_request.llm_api_key
            )
        organization = Organization(**org_request.dict())

        if invoice_settings.stripe_disabled:
            customer = MockStripeCustomer()
            subscription = MockStripeSubscription()
        else:
            customer = self.billing.create_customer(organization.name)
            subscription = self.billing.create_subscription(customer.id)
        # default organization plan is CREDIT_ONLY
        organization.invoice_details = InvoiceDetails(
            plan=PaymentPlan.CREDIT_ONLY,
            stripe_customer_id=customer.id,
            stripe_subscription_id=subscription.id,
            stripe_subscription_status=subscription.status,
            billing_cycle_anchor=subscription.billing_cycle_anchor,
            spending_limit=invoice_settings.default_spending_limit,
            hard_spending_limit=invoice_settings.default_hard_spending_limit,
            available_credits=invoice_settings.signup_credits,
        )
        new_id = self.repo.add_organization(organization)
        if new_id:
            new_organization = self.repo.get_organization(new_id)
            # create signup credit, mark as recorded
            credit_id = self.invoice_repo.create_credit(
                Credit(
                    organization_id=new_id,
                    amount=invoice_settings.signup_credits,
                    status=RecordStatus.RECORDED,
                    description="Signup credits",
                )
            )
            print(f"New credit created: {credit_id}")
            self.analytics.track(
                new_organization.id,
                EventName.organization_created,
                EventType.organization_event(
                    id=new_organization.id,
                    name=new_organization.name,
                    owner=new_organization.owner,
                ),
            )
            return OrganizationResponse(**new_organization.dict())

        raise CannotCreateOrganizationError()

    def add_user_organization(self, user_id: str, user_email: str) -> str:
        new_organization = self.add_organization(
            OrganizationRequest(name=user_email, owner=user_id)
        )
        return new_organization.id

    def update_organization(
        self, org_id: str, org_request: OrganizationRequest
    ) -> OrganizationResponse:
        if org_request.llm_api_key:
            self._validate_api_key(org_request.llm_api_key)
            org_request.llm_api_key = self._encrypt_llm_credentials(
                org_request.llm_api_key
            )
        organization = Organization(**org_request.dict(exclude_unset=True))

        if (
            self.repo.update_organization(org_id, organization.dict(exclude_unset=True))
            == 1
        ):
            self.repo.insert_or_replace_llm_api_key(org_id, org_request.llm_api_key)
            return self.repo.get_organization(org_id)

        raise CannotUpdateOrganizationError(org_id)

    def delete_organization(self, org_id: str) -> dict:
        if self.repo.delete_organization(org_id) == 1:
            return {"id": org_id}

        raise CannotDeleteOrganizationError(org_id)

    def add_organization_by_slack_installation(
        self, slack_installation_request: SlackInstallation
    ) -> OrganizationResponse:
        current_org = self.repo.get_organization_by_slack_workspace_id(
            slack_installation_request.team.id
        )
        if current_org:  # update
            if (
                self.repo.update_organization(
                    str(current_org.id),
                    {
                        "slack_config.slack_installation": slack_installation_request.dict()
                    },
                )
                == 1
            ):
                updated_org = self.repo.get_organization(str(current_org.id))
                return OrganizationResponse(**updated_org.dict())

            raise CannotUpdateOrganizationError(current_org.id)

        organization = Organization(
            name=slack_installation_request.team.name,
            slack_config=SlackConfig(
                slack_installation=slack_installation_request, db_connection_id=None
            ),
            owner=slack_installation_request.user.id,
        )

        if invoice_settings.stripe_disabled:
            customer = MockStripeCustomer()
            subscription = MockStripeSubscription()
        else:
            customer = self.billing.create_customer(organization.name)
            subscription = self.billing.create_subscription(customer.id)
        organization.invoice_details = InvoiceDetails(
            plan=PaymentPlan.CREDIT_ONLY,
            stripe_customer_id=customer.id,
            stripe_subscription_id=subscription.id,
            stripe_subscription_status=subscription.status,
            billing_cycle_anchor=subscription.billing_cycle_anchor,
            spending_limit=invoice_settings.default_spending_limit,
            hard_spending_limit=invoice_settings.default_hard_spending_limit,
            available_credits=invoice_settings.signup_credits,
        )

        new_id = self.repo.add_organization(organization)
        if new_id:
            # create signup credit, mark as recorded
            new_organization = self.repo.get_organization(new_id)
            credit_id = self.invoice_repo.create_credit(
                Credit(
                    organization_id=new_id,
                    amount=invoice_settings.signup_credits,
                    status=RecordStatus.RECORDED,
                    description="Signup credits",
                )
            )
            print(f"New credit created: {credit_id}")
            self.analytics.track(
                new_organization.id,
                EventName.organization_created,
                EventType.organization_event(
                    id=new_organization.id,
                    name=new_organization.name,
                    owner=new_organization.owner,
                ),
            )
            return new_organization

        raise CannotCreateOrganizationError()

    def get_slack_installation_by_slack_workspace_id(
        self, slack_workspace_id: str
    ) -> SlackInstallation:
        organization = self.repo.get_organization_by_slack_workspace_id(
            slack_workspace_id
        )
        if organization:
            return organization.slack_config.slack_installation

        raise SlackInstallationNotFoundError(slack_workspace_id)

    def get_organization_by_customer_id(self, customer_id: str) -> Organization:
        return self.repo.get_organization_by_customer_id(customer_id)

    def _encrypt_llm_credentials(self, llm_api_key: str) -> str:
        fernet_encrypt = FernetEncrypt()
        return fernet_encrypt.encrypt(llm_api_key)

    def _validate_api_key(self, llm_api_key: str):
        openai.api_key = llm_api_key
        try:
            openai.Model.list()
        except openai.error.AuthenticationError as e:
            raise InvalidLlmApiKeyError() from e

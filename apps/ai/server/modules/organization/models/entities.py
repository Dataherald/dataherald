from datetime import datetime

from pydantic import BaseModel, Field, confloat

from modules.organization.invoice.models.entities import InvoiceDetails
from utils.validation import ObjectIdString


class SlackTeam(BaseModel):
    id: str | None
    name: str | None


class SlackUser(BaseModel):
    token: str | None
    scopes: str | None
    id: str | None


class SlackBot(BaseModel):
    scopes: list[str] | None
    token: str | None
    user_id: str | None
    id: str | None


class SlackInstallation(BaseModel):
    team: SlackTeam | None
    enterprise: str | None
    user: SlackUser | None
    token_type: str | None
    is_enterprise_install: bool | None
    app_id: str | None
    auth_version: str | None
    bot: SlackBot | None


class SlackConfig(BaseModel):
    slack_installation: SlackInstallation | None
    db_connection_id: ObjectIdString | None


class BaseOrganization(BaseModel):
    name: str
    confidence_threshold: confloat(ge=0, le=1) = Field(default=1.0)
    slack_config: SlackConfig | None
    llm_api_key: str | None
    owner: str | None


class Organization(BaseOrganization):
    id: ObjectIdString | None
    created_at: datetime | None = datetime.now()
    invoice_details: InvoiceDetails | None

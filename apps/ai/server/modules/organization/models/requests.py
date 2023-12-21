from pydantic import BaseModel, Field

from modules.organization.models.entities import BaseOrganization


class SlackTeamRequest(BaseModel):
    id: str | None
    name: str | None


class SlackUserRequest(BaseModel):
    token: str | None
    scopes: str | None
    id: str | None


class SlackBotRequest(BaseModel):
    scopes: list[str] | None
    token: str | None
    user_id: str | None = Field(alias="userId")
    id: str | None


class SlackInstallationRequest(BaseModel):
    team: SlackTeamRequest | None
    enterprise: str | None
    user: SlackUserRequest | None
    token_type: str | None = Field(alias="tokenType")
    is_enterprise_install: bool | None = Field(alias="isEnterpriseInstall")
    app_id: str | None = Field(alias="appId")
    auth_version: str | None = Field(alias="authVersion")
    bot: SlackBotRequest | None


class OrganizationRequest(BaseOrganization):
    pass

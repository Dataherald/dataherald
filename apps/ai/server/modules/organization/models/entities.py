from typing import Any

from pydantic import BaseModel, Field, confloat


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


class Organization(BaseModel):
    id: Any = Field(alias="_id")
    name: str
    db_alias: str | None
    confidence_threshold: confloat(ge=0, le=1) = 1.0
    slack_installation: SlackInstallation | None

from typing import Any

from pydantic import BaseModel, Field


class User(BaseModel):
    id: Any = Field(alias="_id")
    email: str
    email_verified: bool | None
    name: str | None
    nickname: str | None
    picture: str | None
    organization_id: Any


class SlackQuestionUser(BaseModel):
    slack_id: str | None
    username: str | None
    slack_workspace_id: str | None

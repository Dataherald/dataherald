from typing import Any

from pydantic import BaseModel, Field


class BaseUser(BaseModel):
    email: str
    email_verified: bool | None
    name: str | None
    nickname: str | None
    picture: str | None
    sub: str | None
    updated_at: str | None


class User(BaseUser):
    id: Any = Field(alias="_id")
    organization_id: Any


class SlackInfo(BaseModel):
    user_id: str | None
    channel_id: str | None
    thread_ts: str | None
    username: str | None

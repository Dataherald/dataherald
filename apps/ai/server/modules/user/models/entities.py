from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Roles(str, Enum):
    admin = "ADMIN"


class BaseUser(BaseModel):
    email: str | None
    email_verified: bool | None
    name: str | None
    nickname: str | None
    picture: str | None
    sub: str | None
    updated_at: str | None


class User(BaseUser):
    id: Any = Field(alias="_id")
    organization_id: Any
    role: Roles | None


class SlackInfo(BaseModel):
    user_id: str | None
    channel_id: str | None
    thread_ts: str | None
    username: str | None

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class Roles(str, Enum):
    admin = "ADMIN"


class BaseUser(BaseModel):
    email: str | None
    email_verified: bool | None
    name: str | None
    nickname: str | None
    picture: str | None
    sub: str | None
    updated_at: str | None  # str because its filled by auth0


class User(BaseUser):
    id: str | None
    organization_id: str | None
    role: Roles | None
    created_at: datetime | None = datetime.now()


class SlackInfo(BaseModel):
    user_id: str | None
    channel_id: str | None
    thread_ts: str | None

from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from utils.validation import ObjectIdString


class Roles(str, Enum):
    admin = "ADMIN"


class BaseUser(BaseModel):
    organization_id: ObjectIdString | None
    email: str | None
    email_verified: bool | None
    name: str | None
    nickname: str | None
    picture: str | None
    sub: str | None
    updated_at: str | None  # str because its filled by auth0


class User(BaseUser):
    id: ObjectIdString | None
    role: Roles | None
    created_at: datetime = datetime.now()

from pydantic import Field

from modules.user.models.entities import BaseUser


class UserResponse(BaseUser):
    id: str = Field(alias="_id")
    organization_id: str

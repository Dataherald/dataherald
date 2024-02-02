from pydantic import BaseModel

from modules.user.models.entities import BaseUser


class UserRequest(BaseUser):
    organization_id: str | None
    pass


class UserOrganizationRequest(BaseModel):
    organization_id: str

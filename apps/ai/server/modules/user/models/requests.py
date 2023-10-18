from pydantic import BaseModel

from modules.user.models.entities import BaseUser


class UserRequest(BaseUser):
    pass


class UserOrganizationRequest(BaseModel):
    organization_id: str

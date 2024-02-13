from pydantic import BaseModel

from modules.user.models.entities import BaseUser
from utils.validation import ObjectIdString


class UserRequest(BaseUser):
    pass


class UserOrganizationRequest(BaseModel):
    organization_id: ObjectIdString

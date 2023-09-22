from modules.user.models.entities import BaseUser


class UserResponse(BaseUser):
    id: str
    organization_id: str

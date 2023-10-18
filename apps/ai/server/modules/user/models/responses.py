from modules.user.models.entities import BaseUser, Roles


class UserResponse(BaseUser):
    id: str
    organization_id: str
    role: Roles | None

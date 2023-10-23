from modules.user.models.entities import Roles, User


class UserResponse(User):
    id: str
    organization_id: str
    role: Roles | None

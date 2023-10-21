from modules.user.models.entities import User, Roles


class UserResponse(User):
    id: str
    organization_id: str
    role: Roles | None

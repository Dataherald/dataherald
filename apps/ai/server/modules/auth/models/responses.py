from modules.user.models.entities import User


class AuthUserResponse(User):
    organization_name: str | None

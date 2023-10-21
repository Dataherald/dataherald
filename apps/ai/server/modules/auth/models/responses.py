from typing_extensions import deprecated

from modules.user.models.entities import User


@deprecated("Use User instead")
class AuthUserResponse(User):
    organization_name: str | None

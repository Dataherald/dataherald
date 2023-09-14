from modules.user.models.entities import BaseUser


class AuthUserRequest(BaseUser):
    email: str
    email_verified: bool | None
    name: str | None
    nickname: str | None
    picture: str | None
    sub: str | None
    updated_at: str | None

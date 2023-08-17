from pydantic import BaseModel


class AuthUserRequest(BaseModel):
    email: str
    email_verified: bool | None
    name: str | None
    nickname: str | None
    picture: str | None
    sub: str | None
    updated_at: str | None

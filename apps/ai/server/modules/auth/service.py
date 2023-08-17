from fastapi import HTTPException

from modules.auth.models.requests import AuthUserRequest
from modules.user.models.entities import User
from modules.user.service import UserService


class AuthService:
    def __init__(self):
        self.user_service = UserService()

    def login(self, user_request: AuthUserRequest) -> User:
        login_user = User(**user_request.dict())
        # check if user exists or not
        user = self.user_service.get_user_by_email(login_user.email)
        if user:
            self.user_service.update_user(
                str(user.id),
                login_user.dict(),
                exclude={"id", "email", "organization_id"},
            )

        else:
            raise HTTPException(status_code=401, detail="Unauthorized User")

        # return updated user
        return self.user_service.get_user_by_email(login_user.email)

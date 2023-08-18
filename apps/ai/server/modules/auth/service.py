from fastapi import HTTPException

from modules.auth.models.requests import AuthUserRequest
from modules.auth.models.responses import AuthUserResponse
from modules.organization.service import OrganizationService
from modules.user.models.entities import User
from modules.user.service import UserService


class AuthService:
    def __init__(self):
        self.user_service = UserService()
        self.org_service = OrganizationService()

    def login(self, user_request: AuthUserRequest) -> AuthUserResponse:
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
        new_user = self.user_service.get_user_by_email(login_user.email)
        new_user_id = new_user.id
        # the id does not get transformed into the new pydantic object
        new_user = AuthUserResponse(**new_user.dict())
        new_user.id = new_user_id
        new_user.organization_name = self.org_service.get_organization(
            new_user.organization_id
        ).name

        return new_user

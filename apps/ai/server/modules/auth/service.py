from fastapi import HTTPException, status

from modules.organization.service import OrganizationService
from modules.user.models.requests import UserRequest
from modules.user.models.responses import UserResponse
from modules.user.service import UserService
from utils.analytics import Analytics


class AuthService:
    def __init__(self):
        self.user_service = UserService()
        self.org_service = OrganizationService()
        self.analytics = Analytics()

    def login(self, user_request: UserRequest) -> UserResponse:
        # check if user exists or not
        user = self.user_service.get_user_by_email(user_request.email)
        if user:
            self.user_service.update_user(
                str(user.id),
                UserRequest(**user_request.dict()),
                str(user.organization_id),
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User"
            )

        # return updated user
        new_user = self.user_service.get_user_by_email(user_request.email)
        new_user_id = new_user.id
        # the id does not get transformed into the new pydantic object
        new_user = UserResponse(**new_user.dict())
        new_user.id = new_user_id

        self.analytics.identify(
            str(new_user.email),
            {
                "email": new_user.email,
                "name": new_user.name,
                "organization_id": str(new_user.organization_id),
                "organization_name": self.org_service.get_organization(
                    str(new_user.organization_id)
                ).name,
            },
        )
        return new_user

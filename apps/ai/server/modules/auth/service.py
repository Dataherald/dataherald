from modules.organization.models.entities import Organization
from modules.organization.service import OrganizationService
from modules.user.models.requests import UserRequest
from modules.user.models.responses import UserResponse
from modules.user.service import UserService
from utils.analytics import Analytics, OrganizationProperties, UserProperties


class AuthService:
    def __init__(self):
        self.user_service = UserService()
        self.org_service = OrganizationService()
        self.analytics = Analytics()

    def login(self, user_request: UserRequest) -> UserResponse:
        # check if user exists or not
        user_org_id = None
        user = self.user_service.get_user_by_email(user_request.email)

        if not user:  # create the user and a new organization for the user
            user = self.user_service.add_user(user_request)
            user_org_id = self.org_service.add_user_organization(user.id, user.email)
        elif user.organization_id is None:
            user_org_id = self.org_service.add_user_organization(user.id, user.email)
        else:
            user_org_id = user.organization_id

        # update user data from the login request cause it could have updates
        # TODO - when we add user data customization, we should stop doing this
        session_user = self.user_service.update_user(
            str(user.id),
            UserRequest(
                **{
                    **user_request.dict(exclude={"organization_id"}),
                    "organization_id": user_org_id,
                }
            ),
        )

        organization = (
            self.org_service.get_organization(str(session_user.organization_id))
            if session_user.organization_id
            else Organization(name=None, id=None, owner=None)
        )

        self.analytics.identify(
            str(session_user.email),
            UserProperties(
                email=session_user.email,
                name=session_user.name,
                organization_id=organization.id,
                organization_name=organization.name,
            ),
        )

        if organization.id:
            self.analytics.identify(
                user_org_id,
                OrganizationProperties(
                    id=user_org_id,
                    name=organization.name,
                    owner=organization.owner,
                ),
            )

        return session_user

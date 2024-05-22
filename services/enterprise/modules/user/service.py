from bson import ObjectId

from modules.user.models.entities import User
from modules.user.models.exceptions import (
    CannotCreateUserError,
    CannotDeleteLastUserError,
    CannotDeleteUserError,
    CannotUpdateUserError,
    UserExistsInOrgError,
    UserExistsInOtherOrgError,
    UserNotFoundError,
)
from modules.user.models.requests import UserOrganizationRequest, UserRequest
from modules.user.models.responses import UserResponse
from modules.user.repository import UserRepository
from utils.analytics import Analytics, EventName, EventType


class UserService:
    def __init__(self):
        self.repo = UserRepository()
        self.analytics = Analytics()

    def get_users(self, org_id: str) -> list[UserResponse]:
        users = self.repo.get_users({"organization_id": org_id})
        return [UserResponse(**user.dict()) for user in users]

    def get_user(self, user_id: str, org_id: str) -> UserResponse:
        return self.get_user_in_org(user_id, org_id)

    def get_user_by_sub(self, sub: str) -> User:
        """Helper function to get user by Auth0sub."""
        user = self.repo.get_user_by_sub(sub)
        return user if user else None

    def get_user_by_email(self, email: str) -> User:
        """Helper function to get user by email."""
        user = self.repo.get_user_by_email(email)
        return user if user else None

    def add_user(self, user_request: UserRequest) -> UserResponse:
        self.check_user_exists(user_request.email, user_request.organization_id)
        new_user = User(**user_request.dict())
        new_user_id = self.repo.add_user(new_user)
        if new_user_id:
            added_user = self.repo.get_user({"_id": ObjectId(new_user_id)})
            return UserResponse(**added_user.dict())

        raise CannotCreateUserError(user_request.organization_id)

    def invite_user_to_org(
        self, user_request: UserRequest, org_id: str
    ) -> UserResponse:
        self.check_user_exists(user_request.email, org_id)

        new_user_data = User(
            **user_request.dict(exclude={"organization_id"}), organization_id=org_id
        )
        new_user_id = self.repo.add_user(new_user_data)
        if not new_user_id:
            raise CannotCreateUserError(org_id)

        new_user = self.repo.get_user({"_id": ObjectId(new_user_id)})

        self.analytics.track(
            org_id,
            EventName.user_invited,
            EventType.user_event(
                id=new_user.id,
                email=new_user.email,
                name=new_user.name,
                organization_id=new_user.organization_id,
            ),
        )

        return UserResponse(**new_user.dict())

    def update_user(self, user_id: str, user_request: UserRequest) -> UserResponse:
        if (
            self.repo.update_user(
                {"_id": ObjectId(user_id)},
                user_request.dict(exclude_unset=True),
            )
            == 1
        ):
            new_user = self.repo.get_user({"_id": ObjectId(user_id)})
            return UserResponse(**new_user.dict())

        raise CannotUpdateUserError(user_id, user_request.organization_id)

    def update_user_organization(
        self, user_id: str, user_organization_request: UserOrganizationRequest
    ) -> UserResponse:
        if (
            self.repo.update_user(
                {"_id": ObjectId(user_id)},
                {"organization_id": user_organization_request.organization_id},
            )
            == 1
        ):
            new_user = self.repo.get_user({"_id": ObjectId(user_id)})
            return UserResponse(**new_user.dict())

        raise CannotUpdateUserError(user_id, user_organization_request.organization_id)

    def delete_user(self, user_id: str, org_id: str) -> dict:
        if (
            len(
                self.repo.get_users(
                    {"organization_id": org_id, "role": {"$ne": "ADMIN"}}
                )
            )
            > 1
        ):
            if (
                self.repo.delete_user(
                    {"_id": ObjectId(user_id), "organization_id": org_id}
                )
                == 1
            ):
                return {"id": user_id}

            raise CannotDeleteUserError(user_id, org_id)

        raise CannotDeleteLastUserError(user_id, org_id)

    def get_user_in_org(self, user_id: str, org_id: str) -> User:
        user = self.repo.get_user({"_id": ObjectId(user_id), "organization_id": org_id})
        if not user:
            raise UserNotFoundError(user_id, org_id)
        return user

    def check_user_exists(self, email: str, org_id: str):
        stored_user = self.repo.get_user_by_email(email)
        if stored_user:
            if stored_user.organization_id == org_id:
                raise UserExistsInOrgError(stored_user.id, org_id)
            raise UserExistsInOtherOrgError(stored_user.id, stored_user.organization_id)

from bson import ObjectId
from fastapi import HTTPException, status

from modules.user.models.entities import User
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
        user = self.repo.get_user({"_id": ObjectId(user_id), "organization_id": org_id})
        return UserResponse(**user.dict()) if user else None

    def get_user_by_email(self, email: str) -> UserResponse:
        user = self.repo.get_user_by_email(email)
        if user:
            return UserResponse(**user.dict())
        return None

    def add_user(self, user_request: UserRequest) -> UserResponse:
        new_user = User(**user_request.dict())
        new_user_id = self.repo.add_user(new_user)
        if new_user_id:
            added_user = self.repo.get_user({"_id": ObjectId(new_user_id)})
            return UserResponse(**added_user.dict())

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User exists or cannot add user",
        )

    def invite_user_to_org(
        self, user_request: UserRequest, org_id: str
    ) -> UserResponse:
        stored_user = self.repo.get_user_by_email(user_request.email)
        if stored_user:
            if stored_user.organization_id == org_id:
                error_code = "USER_ALREADY_EXISTS_IN_ORG"
            else:
                error_code = "USER_ALREADY_EXISTS_IN_OTHER_ORG"

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_code,
            )

        new_user_data = User(
            **user_request.dict(exclude={"organization_id"}), organization_id=org_id
        )
        new_user_id = self.repo.add_user(new_user_data)
        if not new_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An error occurred while trying to create the user",
            )

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

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found or cannot be updated",
        )

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

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found or cannot be updated",
        )

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

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found or cannot be deleted",
        )

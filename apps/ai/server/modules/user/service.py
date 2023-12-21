from datetime import datetime

from bson import ObjectId
from fastapi import HTTPException, status

from modules.user.models.entities import User
from modules.user.models.requests import UserOrganizationRequest, UserRequest
from modules.user.models.responses import UserResponse
from modules.user.repository import UserRepository


class UserService:
    def __init__(self):
        self.repo = UserRepository()

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

    def add_user(self, user_request: UserRequest, org_id: str) -> UserResponse:
        new_user_data = User(
            **user_request.dict(), organization_id=org_id, created_at=datetime.now()
        )
        new_id = self.repo.add_user(new_user_data.dict(exclude_unset=True))
        if new_id:
            new_user = self.repo.get_user({"_id": ObjectId(new_id)})
            return UserResponse(**new_user.dict())

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User exists or cannot add user",
        )

    def update_user(
        self, user_id: str, user_request: UserRequest, org_id: str
    ) -> UserResponse:
        if (
            self.repo.update_user(
                {"_id": ObjectId(user_id), "organization_id": org_id},
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
                    {"organization_id": ObjectId(org_id), "role": {"$ne": "ADMIN"}}
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

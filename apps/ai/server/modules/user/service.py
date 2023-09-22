from bson import ObjectId
from fastapi import HTTPException

from modules.user.models.entities import User
from modules.user.models.requests import UserRequest
from modules.user.models.responses import UserResponse
from modules.user.repository import UserRepository


class UserService:
    def __init__(self):
        self.repo = UserRepository()

    def get_users(self, org_id: str) -> list[UserResponse]:
        filter = {"organization_id": ObjectId(org_id)} if org_id else None
        users = self.repo.get_users(filter)
        return [self._get_mapped_user_response(user) for user in users]

    def get_user(self, user_id: str) -> UserResponse:
        user = self.repo.get_user(user_id)
        return self._get_mapped_user_response(user) if user else None

    def get_user_by_email(self, email: str) -> UserResponse:
        user = self.repo.get_user_by_email(email)
        if user:
            return self._get_mapped_user_response(user)
        return None

    def add_user(self, user_request: UserRequest, org_id: str) -> UserResponse:
        new_user_data = User(**user_request.dict())
        new_user_data.organization_id = ObjectId(org_id)
        new_id = self.repo.add_user(new_user_data.dict(exclude={"id"}))
        if new_id:
            new_user = self.repo.get_user(new_id)
            return self._get_mapped_user_response(new_user)

        raise HTTPException(status_code=400, detail="User exists or cannot add user")

    def update_user(self, user_id: str, user_request: UserRequest) -> UserResponse:
        if self.repo.update_user(user_id, user_request.dict()) == 1:
            new_user = self.repo.get_user(user_id)
            return self._get_mapped_user_response(new_user)

        raise HTTPException(
            status_code=400, detail="User not found or cannot be updated"
        )

    def delete_user(self, user_id: str) -> dict:
        if self.repo.delete_user(user_id) == 1:
            return {"id": user_id}

        raise HTTPException(
            status_code=400, detail="User not found or cannot be deleted"
        )

    def _get_mapped_user_response(self, user: User) -> UserResponse:
        user.id = str(user.id)
        user.organization_id = str(user.organization_id)
        user_dict = user.dict()
        user_dict["id"] = str(user_dict["id"])
        user_dict["organization_id"] = str(user_dict["organization_id"])
        return UserResponse(**user_dict)

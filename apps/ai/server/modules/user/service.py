from bson import ObjectId
from fastapi import HTTPException

from modules.user.models.entities import User
from modules.user.repository import UserRepository


class UserService:
    def __init__(self):
        self.repo = UserRepository()

    def get_users(self, org_id: ObjectId) -> list[User]:
        filter = {"organization_id": org_id} if org_id else None
        users = self.repo.get_users(filter)
        for user in users:
            self._ids_to_str(user)
        return users

    def get_user(self, id: str) -> User:
        user = self.repo.get_user(id)
        if user:
            self._ids_to_str(user)
            return user
        return None

    def get_user_by_email(self, email: str) -> User:
        user = self.repo.get_user_by_email(email)
        if user:
            self._ids_to_str(user)
            return user
        return None

    def delete_user(self, id: str):
        if self.repo.delete_user(id) == 1:
            return {"id": id}

        raise HTTPException(
            status_code=400, detail="User not found or cannot be deleted"
        )

    def update_user(self, id: str, user_data: dict, exclude: set = None) -> User:
        new_user_data = User(**user_data)
        self._ids_to_str(new_user_data)
        if self.repo.update_user(id, new_user_data.dict(exclude=exclude)) == 1:
            new_user = self.repo.get_user(id)
            self._ids_to_str(new_user)
            return new_user

        raise HTTPException(
            status_code=400, detail="User not found or cannot be updated"
        )

    def add_user(self, user_data: dict, org_id: ObjectId) -> User:
        new_user_data = User(**user_data)
        new_user_data.organization_id = org_id
        new_id = self.repo.add_user(new_user_data.dict(exclude={"id"}))
        if new_id:
            new_user = self.repo.get_user(new_id)
            self._ids_to_str(new_user)
            return new_user

        raise HTTPException(status_code=400, detail="User exists or cannot add user")

    def _ids_to_str(self, user: User):
        user.id = str(user.id)
        user.organization_id = str(user.organization_id)

from fastapi import HTTPException

from modules.user.models.entities import User
from modules.user.repository import UserRepository


class UserService:
    def __init__(self):
        self.repo = UserRepository()

    def list_users(self, org_id: str) -> list[User]:
        filter = {"organization_id": org_id} if org_id else None
        users = self.repo.list_users(filter)
        for user in users:
            user.id = str(user.id)
        return users

    def get_user(self, id: str) -> User:
        user = self.repo.get_user(id)
        if user:
            user.id = str(user.id)
            return user
        return None

    def get_user_by_email(self, email: str) -> User:
        user = self.repo.get_user_by_email(email)
        if user:
            user.id = str(user.id)
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
        new_user_data.id = id
        if self.repo.update_user(id, new_user_data.dict(exclude=exclude)) == 1:
            return new_user_data

        raise HTTPException(
            status_code=400, detail="User not found or cannot be updated"
        )

    def add_user(self, user_data: dict) -> User:
        new_user_data = User(**user_data)
        new_id = self.repo.add_user(new_user_data.dict(exclude={"id"}))
        new_user_data.id = str(new_id)
        if new_id:
            return new_user_data

        raise HTTPException(status_code=400, detail="User exists or cannot add user")

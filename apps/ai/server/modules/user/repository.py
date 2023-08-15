from bson import ObjectId

from config import USER_COL
from database.mongo import MongoDB
from modules.user.models.entities import User


class UserRepository:
    def list_users(self, filter: dict) -> list[User]:
        return [User(**user) for user in MongoDB.find(USER_COL, filter)]

    def get_user(self, id: str) -> User:
        return User(**MongoDB.find_by_id(USER_COL, id))

    def delete_user(self, id: str) -> int:
        return MongoDB.delete_one("user", {"_id": ObjectId(id)})

    def update_user(self, id: str, new_user_data: dict) -> int:
        return MongoDB.update_one(USER_COL, {"_id": ObjectId(id)}, new_user_data)

    def add_user(self, new_user_data: dict) -> int:
        if MongoDB.find_one(USER_COL, {"email": new_user_data["email"]}):
            return None
        return MongoDB.insert_one(USER_COL, new_user_data)

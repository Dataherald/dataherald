from config import USER_COL
from database.mongo import MongoDB
from modules.user.models.entities import User


class UserRepository:
    def get_users(self, query: dict) -> list[User]:
        return [
            User(id=str(user["_id"]), **user) for user in MongoDB.find(USER_COL, query)
        ]

    def get_user(self, query: dict) -> User:
        user = MongoDB.find_one(USER_COL, query)
        return User(id=str(user["_id"]), **user) if user else None

    def get_user_by_sub(self, sub: str) -> User:
        user = MongoDB.find_one(USER_COL, {"sub": sub})
        return User(id=str(user["_id"]), **user) if user else None

    def get_user_by_email(self, email: str) -> User:
        user = MongoDB.find_one(USER_COL, {"email": email})
        return User(id=str(user["_id"]), **user) if user else None

    def delete_user(self, query: dict) -> int:
        return MongoDB.delete_one(USER_COL, query)

    def update_user(self, query: dict, new_user_data: dict) -> int:
        return MongoDB.update_one(USER_COL, query, new_user_data)

    def add_user(self, new_user: User) -> str:
        if MongoDB.find_one(USER_COL, {"email": new_user.email}):
            return None
        return str(MongoDB.insert_one(USER_COL, new_user.dict(exclude={"id"})))

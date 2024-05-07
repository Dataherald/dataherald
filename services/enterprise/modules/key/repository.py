from bson import ObjectId

from config import KEY_COL
from database.mongo import MongoDB
from modules.key.models.entities import APIKey


class KeyRepository:
    def get_key(self, key_id: str, org_id: str) -> APIKey:
        key = MongoDB.find_one(
            KEY_COL, {"_id": ObjectId(key_id), "organization_id": org_id}
        )
        return APIKey(id=str(key["_id"]), **key) if key else None

    def get_key_by_name(self, name: str, org_id: str) -> APIKey:
        key = MongoDB.find_one(KEY_COL, {"name": name, "organization_id": org_id})
        return APIKey(id=str(key["_id"]), **key) if key else None

    def get_keys(self, org_id: str) -> list[APIKey]:
        return [
            APIKey(id=str(key["_id"]), **key)
            for key in MongoDB.find(KEY_COL, {"organization_id": org_id})
        ]

    def get_key_by_hash(self, key_hash: str) -> APIKey:
        key = MongoDB.find_one(KEY_COL, {"key_hash": key_hash})
        return APIKey(id=str(key["_id"]), **key) if key else None

    def add_key(self, key: APIKey) -> str:
        return str(MongoDB.insert_one(KEY_COL, key.dict(exclude={"id"})))

    def delete_key(self, key_id: str, org_id: str) -> int:
        return MongoDB.delete_one(
            KEY_COL, {"_id": ObjectId(key_id), "organization_id": org_id}
        )

from bson import ObjectId

from config import DATABASE_CONNECTION_COL, DATABASE_CONNECTION_REF_COL
from database.mongo import MongoDB
from modules.db_connection.models.entities import DBConnection, DBConnectionRef


class DatabaseRepository:
    def get_db_connections(self, db_connection_ids: list[str]) -> list[DBConnection]:
        object_ids = [ObjectId(id) for id in db_connection_ids]
        db_connections = MongoDB.find_by_object_ids(DATABASE_CONNECTION_COL, object_ids)
        return [DBConnection(**db_connection) for db_connection in db_connections]

    def get_db_connection(self, db_connection_id: str) -> DBConnection:
        db_connection = MongoDB.find_by_id(
            DATABASE_CONNECTION_COL, ObjectId(db_connection_id)
        )
        return DBConnection(**db_connection) if db_connection else None

    def get_db_connection_refs(self, org_id: str) -> list[DBConnectionRef]:
        return MongoDB.find(
            DATABASE_CONNECTION_REF_COL, {"organization_id": ObjectId(org_id)}
        )

    def add_db_connection_ref(
        self,
        db_connection_ref_data: dict,
    ) -> str:
        str(MongoDB.insert_one(DATABASE_CONNECTION_REF_COL, db_connection_ref_data))

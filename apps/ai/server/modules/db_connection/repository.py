from bson import ObjectId

from config import DATABASE_CONNECTION_COL
from database.mongo import MongoDB
from modules.db_connection.models.entities import DBConnection


class DBConnectionRepository:
    def get_db_connections(self, org_id: str) -> list[DBConnection]:
        db_connections = MongoDB.find(
            DATABASE_CONNECTION_COL,
            {"metadata.dh_internal.organization_id": org_id},
        )
        return [
            DBConnection(id=str(db_connection["_id"]), **db_connection)
            for db_connection in db_connections
        ]

    def get_db_connection(self, db_connection_id: str, org_id: str) -> DBConnection:
        db_connection = MongoDB.find_one(
            DATABASE_CONNECTION_COL,
            {
                "_id": ObjectId(db_connection_id),
                "metadata.dh_internal.organization_id": org_id,
            },
        )
        return (
            DBConnection(id=str(db_connection["_id"]), **db_connection)
            if db_connection
            else None
        )

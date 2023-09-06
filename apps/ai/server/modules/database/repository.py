from config import DATABASE_CONNECTION_REF_COL
from database.mongo import MongoDB


class DatabaseRepository:
    def add_database_connection_ref(
        self,
        database_connection_ref_data: dict,
    ) -> str:
        str(
            MongoDB.insert_one(
                DATABASE_CONNECTION_REF_COL, database_connection_ref_data
            )
        )

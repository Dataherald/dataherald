from modules.db_connection.models.responses import DatabaseResponse
from modules.db_connection.repository import DBConnectionRepository


class DBConnectionService:
    def __init__(self):
        self.repo = DBConnectionRepository()

    def get_databases(self) -> list[DatabaseResponse]:
        cursor = self.repo.get_databases()
        return [DatabaseResponse(alias=db["alias"]) for db in cursor]

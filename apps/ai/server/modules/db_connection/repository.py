from config import DB_CONNECTION_COL
from database.mongo import MongoDB


class DBConnectionRepository:
    def get_databases(self):
        return MongoDB.find(DB_CONNECTION_COL, {})

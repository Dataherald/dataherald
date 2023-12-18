from dataherald.db_scanner.models.types import QueryHistory

DB_COLLECTION = "query_history"


class QueryHistoryRepository:
    def __init__(self, storage):
        self.storage = storage

    def insert(self, query_history: QueryHistory) -> QueryHistory:
        query_history_dict = query_history.dict(exclude={"id"})
        query_history_dict["db_connection_id"] = str(query_history.db_connection_id)
        query_history.id = str(
            self.storage.insert_one(DB_COLLECTION, query_history_dict)
        )
        return query_history

    def find_by(
        self, query: dict, page: int = 1, limit: int = 10
    ) -> list[QueryHistory]:
        rows = self.storage.find(DB_COLLECTION, query, page=page, limit=limit)
        result = []
        for row in rows:
            row["id"] = str(row["_id"])
            row["db_connection_id"] = str(row["db_connection_id"])
            result.append(QueryHistory(**row))
        return result

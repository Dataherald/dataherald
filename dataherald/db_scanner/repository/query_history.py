from bson.objectid import ObjectId

from dataherald.db_scanner.models.types import QueryHistory

DB_COLLECTION = "query_history"


class QueryHistoryRepository:
    def __init__(self, storage):
        self.storage = storage

    def insert(self, query_history: QueryHistory) -> QueryHistory:
        query_history_dict = query_history.dict(exclude={"id"})
        query_history_dict["db_connection_id"] = ObjectId(
            query_history.db_connection_id
        )
        query_history.id = str(
            self.storage.insert_one(DB_COLLECTION, query_history_dict)
        )
        return query_history

    # def find_one(self, query: dict) -> Response | None:
    #     if not row:
    #
    # def update(self, response: Response) -> Response:
    #
    #     self.storage.update_or_create(
    #         DB_COLLECTION,
    #         response_dict,
    #
    # def find_by_id(self, id: str) -> Response | None:
    #     if not row:
    #
    # def find_by(self, query: dict, page: int = 1, limit: int = 10) -> list[Response]:
    #         DB_COLLECTION,
    #         query,
    #     for row in rows:
    #

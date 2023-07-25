import pymongo

from database.mongo import MongoDB


class QueriesRepository:
    # temp name
    collection = "queries"

    def get_query(self, db_alias: str, query_id: str):  # noqa: ARG002
        # placeholder
        MongoDB().find_by_id(self.collection, query_id)

    def get_queries(
        self, db_alias: str, order: str, limit: int, skip: int, ascend: bool
    ):
        cursor = MongoDB().find(self.collection, {"db_alias": db_alias})

        sort_direction = pymongo.ASCENDING if ascend else pymongo.DESCENDING

        cursor.sort(order, sort_direction).skip(skip).limit(limit)

        return list(cursor)

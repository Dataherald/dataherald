from modules.queries.repository import QueriesRepository


class QueriesService:
    def get_query(self, db_alias, query_id):
        return QueriesRepository.get_query(db_alias, query_id)

    def get_queries(
        self,
        db_alias: str,
        order: str,
        limit: int,
        skip: int,
        ascend: bool,
    ):
        return QueriesRepository.get_queries(db_alias, order, limit, skip, ascend)

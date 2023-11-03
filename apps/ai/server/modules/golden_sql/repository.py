from bson import ObjectId

from config import GOLDEN_SQL_COL, GOLDEN_SQL_REF_COL, QUERY_RESPONSE_REF_COL
from database.mongo import DESCENDING, MongoDB
from modules.golden_sql.models.entities import GoldenSQL, GoldenSQLRef
from utils.misc import get_next_display_id


class GoldenSQLRepository:
    def get_golden_sql(self, golden_id: str) -> GoldenSQL:
        golden_sql = MongoDB.find_by_object_id(GOLDEN_SQL_COL, ObjectId(golden_id))
        return GoldenSQL(**golden_sql) if golden_sql else None

    def get_golden_sqls(self, golden_ids: list[str]) -> list[GoldenSQL]:
        object_ids = [ObjectId(id) for id in golden_ids]
        golden_sqls = MongoDB.find_by_object_ids(GOLDEN_SQL_COL, object_ids)
        return [GoldenSQL(**gs) for gs in golden_sqls]

    def get_golden_sql_ref(self, golden_id: str) -> GoldenSQLRef:
        golden_sql_ref = MongoDB.find_one(
            GOLDEN_SQL_REF_COL, {"golden_sql_id": ObjectId(golden_id)}
        )
        return GoldenSQLRef(**golden_sql_ref) if golden_sql_ref else None

    def get_golden_sql_refs(
        self, skip: int, limit: int, order: str, org_id: str
    ) -> list[GoldenSQLRef]:
        golden_sql_refs = (
            MongoDB.find(GOLDEN_SQL_REF_COL, {"organization_id": ObjectId(org_id)})
            .sort([(order, DESCENDING)])
            .skip(skip)
            .limit(limit)
        )
        return [GoldenSQLRef(**gsr) for gsr in golden_sql_refs]

    def get_verified_golden_sql_ref(self, query_id: str) -> GoldenSQLRef:
        golden_sql_ref = MongoDB.find_one(
            GOLDEN_SQL_REF_COL, {"query_id": ObjectId(query_id)}
        )
        return GoldenSQLRef(**golden_sql_ref) if golden_sql_ref else None

    def add_golden_sql_ref(
        self,
        golden_sql_ref_data: dict,
    ) -> str:
        return str(
            MongoDB.insert_one(GOLDEN_SQL_REF_COL, golden_sql_ref_data),
        )

    def delete_golden_sql_ref(self, golden_id: str) -> int:
        return MongoDB.delete_one(
            GOLDEN_SQL_REF_COL, {"golden_sql_id": ObjectId(golden_id)}
        )

    # this violates the architecture, but it's a quick fix for now
    # TODO: need to avoid cross resource dependency and avoid circular dependency
    def delete_verified_golden_sql_ref(self, query_id: str):
        return MongoDB.delete_one(GOLDEN_SQL_REF_COL, {"query_id": ObjectId(query_id)})

    def update_query_status(self, query_id: str, status: str):
        # this violates the architecture, but it's a quick fix for now
        # TODO: need to avoid cross resource dependency and avoid circular dependency
        return MongoDB.update_one(
            QUERY_RESPONSE_REF_COL,
            {"_id": ObjectId(query_id)},
            {"status": status},
        )

    def get_next_display_id(self, org_id: str) -> str:
        return get_next_display_id(GOLDEN_SQL_REF_COL, ObjectId(org_id), "GS")

    def get_verified_query_display_id(self, query_id: str) -> str:
        query_ref = MongoDB.find_one(
            QUERY_RESPONSE_REF_COL, {"_id": ObjectId(query_id)}
        )

        if not query_ref:
            return None

        if "display_id" not in query_ref:
            return "QR-00000"

        return query_ref["display_id"]

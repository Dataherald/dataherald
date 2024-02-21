import re

from bson import ObjectId

from config import GOLDEN_SQL_COL, PROMPT_COL
from database.mongo import ASCENDING, DESCENDING, MongoDB
from modules.golden_sql.models.entities import GoldenSQL
from utils.misc import get_next_display_id


class GoldenSQLRepository:
    def get_golden_sql(self, golden_id: str, org_id: str) -> GoldenSQL:
        golden_sql = MongoDB.find_one(
            GOLDEN_SQL_COL,
            {
                "_id": ObjectId(golden_id),
                "metadata.dh_internal.organization_id": org_id,
            },
        )
        return (
            GoldenSQL(id=str(golden_sql["_id"]), **golden_sql) if golden_sql else None
        )

    def get_golden_sqls(
        self,
        skip: int,
        limit: int,
        order: str,
        ascend: bool,
        org_id: str,
        search_term: str = "",
        db_connection_id: str = None,
    ) -> list[GoldenSQL]:
        search_term = re.escape(search_term)
        query = {
            "metadata.dh_internal.organization_id": org_id,
            "$or": [
                {"prompt_text": {"$regex": search_term, "$options": "i"}},
                {"sql": {"$regex": search_term, "$options": "i"}},
            ],
        }
        if db_connection_id:
            query["db_connection_id"] = db_connection_id
        golden_sqls = (
            MongoDB.find(GOLDEN_SQL_COL, query)
            .sort([(order, ASCENDING if ascend else DESCENDING)])
            .skip(skip)
            .limit(limit)
        )
        return [
            GoldenSQL(id=str(golden_sql["_id"]), **golden_sql)
            for golden_sql in golden_sqls
        ]

    def get_verified_golden_sql(self, prompt_id: str) -> GoldenSQL:
        golden_sql = MongoDB.find_one(
            GOLDEN_SQL_COL, {"metadata.dh_internal.prompt_id": prompt_id}
        )
        return (
            GoldenSQL(id=str(golden_sql["_id"]), **golden_sql) if golden_sql else None
        )

    def update_generation_status(self, prompt_id: str, status: str):
        # this violates the architecture, but it's a quick fix for now
        # TODO: need to avoid cross resource dependency and avoid circular dependency
        return MongoDB.update_one(
            PROMPT_COL,
            {"_id": ObjectId(prompt_id)},
            {"metadata.dh_internal.generation_status": status},
        )

    def get_next_display_id(self, org_id: str) -> str:
        return get_next_display_id(GOLDEN_SQL_COL, org_id, "GS")

    def get_verified_query_display_id(self, query_id: str) -> str:
        query_ref = MongoDB.find_one(PROMPT_COL, {"_id": ObjectId(query_id)})

        if not query_ref:
            return None

        if "display_id" not in query_ref:
            return "QR-00000"

        return query_ref["display_id"]

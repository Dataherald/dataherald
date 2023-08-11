from datetime import datetime, timezone

from bson import ObjectId

from config import QUERY_RESPONSE_REF_COL
from database.mongo import MongoDB
from modules.k2_core.models.requests import SlackQuestionUser
from modules.query.models.entities import QueryRef


class K2CoreRepository:
    def record_response_pointer(self, object_id: ObjectId, user: SlackQuestionUser):
        if not MongoDB.find_one(
            QUERY_RESPONSE_REF_COL,
            {"query_response_id": ObjectId(object_id["$oid"])},
        ):
            current_utc_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            query_ptr = QueryRef(
                query_response_id=ObjectId(object_id["$oid"]),
                user=user,
                question_date=current_utc_time,
                last_updated=current_utc_time,
            )
            MongoDB.insert_one(QUERY_RESPONSE_REF_COL, query_ptr.dict(exclude={"id"}))

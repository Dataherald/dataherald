from datetime import datetime, timezone

from bson import ObjectId

from config import QUERY_RESPONSE_REF_COL
from database.mongo import MongoDB
from modules.query.models.entities import QueryRef
from modules.user.models.entities import SlackQuestionUser
from utils.misc import get_next_display_id


class K2CoreRepository:
    def add_query_response_ref(
        self,
        query_id: ObjectId,
        org_id: ObjectId,
        user: SlackQuestionUser,
        display_id: str,
    ):
        current_utc_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        query_ptr = QueryRef(
            query_response_id=query_id,
            user=user,
            question_date=current_utc_time,
            last_updated=current_utc_time,
            organization_id=org_id,
            display_id=display_id,
        )
        MongoDB.insert_one(QUERY_RESPONSE_REF_COL, query_ptr.dict(exclude={"id"}))

    def get_next_display_id(self, org_id: ObjectId) -> str:
        return get_next_display_id(QUERY_RESPONSE_REF_COL, org_id, "QR")

from bson import ObjectId

from config import QUERY_RESPONSE_REF_COL
from database.mongo import MongoDB
from utils.misc import get_next_display_id


class K2CoreRepository:
    def add_query_response_ref(
        self,
        query_response_ref_data: dict,
    ) -> str:
        str(MongoDB.insert_one(QUERY_RESPONSE_REF_COL, query_response_ref_data))

    def get_next_display_id(self, org_id: ObjectId) -> str:
        return get_next_display_id(QUERY_RESPONSE_REF_COL, org_id, "QR")

from datetime import datetime, timezone

from bson.objectid import ObjectId

from config import QUERY_RESPONSE_COL, QUERY_RESPONSE_REF_COL, QUESTION_COL
from database.mongo import MongoDB
from modules.k2_core.models.responses import NLQueryResponse
from modules.query.models.entities import QueryRef, Question


class QueriesRepository:
    def get_question(self, query_id: ObjectId) -> Question:
        query_id = self._get_object_id(query_id)
        return Question(**MongoDB.find_by_object_id(QUESTION_COL, query_id))

    def get_questions(self, query_ids: list[ObjectId]) -> list[Question]:
        questions = MongoDB.find_by_object_ids(QUESTION_COL, query_ids)
        return [Question(**q) for q in questions]

    def get_query_response(self, query_id: ObjectId) -> NLQueryResponse:
        query_id = self._get_object_id(query_id)
        return NLQueryResponse(
            **MongoDB.find_by_object_id(QUERY_RESPONSE_COL, query_id)
        )

    def get_query_responses(self, query_ids) -> list[NLQueryResponse]:
        response_query = {"_id": {"$in": query_ids}}
        query_responses = MongoDB.find(QUERY_RESPONSE_COL, response_query)
        return [NLQueryResponse(**qr) for qr in query_responses]

    def get_query_response_ref(self, query_id: ObjectId) -> QueryRef:
        query_id = self._get_object_id(query_id)
        return QueryRef(
            **MongoDB.find_one(QUERY_RESPONSE_REF_COL, {"query_response_id": query_id})
        )

    def get_query_response_refs(self, skip, limit) -> list[QueryRef]:
        query_refs = MongoDB.find(QUERY_RESPONSE_REF_COL, {}).skip(skip).limit(limit)
        return [QueryRef(**qrr) for qrr in query_refs]

    def update_last_updated(self, query_id: ObjectId):
        query_id = self._get_object_id(query_id)
        current_utc_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        MongoDB.update_one(
            QUERY_RESPONSE_REF_COL,
            {"query_response_id": query_id},
            {"last_updated": current_utc_time},
        )

    # temporary fix for cases where { '$oid': '1234567890' } is either a dict or ObjectId,
    # I believe it is both bson and mongo's issue
    def _get_object_id(self, id):
        if not isinstance(id, ObjectId):
            return ObjectId(id["$oid"])
        return id

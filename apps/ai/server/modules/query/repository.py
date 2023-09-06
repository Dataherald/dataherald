from bson import ObjectId

from config import QUERY_RESPONSE_COL, QUERY_RESPONSE_REF_COL, QUESTION_COL
from database.mongo import DESCENDING, MongoDB
from modules.k2_core.models.responses import NLQueryResponse
from modules.query.models.entities import QueryRef, Question


class QueryRepository:
    def get_question(self, question_id: str) -> Question:
        question = MongoDB.find_by_id(QUESTION_COL, ObjectId(question_id))
        return Question(**question) if question else None

    def get_questions(self, question_ids: list[str]) -> list[Question]:
        object_ids = [ObjectId(id) for id in question_ids]
        questions = MongoDB.find_by_object_ids(QUESTION_COL, object_ids)
        return [Question(**q) for q in questions]

    def get_query_response(self, query_id: str) -> NLQueryResponse:
        query_response = MongoDB.find_by_object_id(
            QUERY_RESPONSE_COL, ObjectId(query_id)
        )
        return NLQueryResponse(**query_response) if query_response else None

    def get_query_responses(self, query_ids: list[str]) -> list[NLQueryResponse]:
        object_ids = [ObjectId(id) for id in query_ids]
        response_query = {"_id": {"$in": object_ids}}
        query_responses = MongoDB.find(QUERY_RESPONSE_COL, response_query)
        return [NLQueryResponse(**qr) for qr in query_responses]

    def get_query_response_ref(self, query_id: str) -> QueryRef:
        query_ref = MongoDB.find_one(
            QUERY_RESPONSE_REF_COL, {"query_response_id": ObjectId(query_id)}
        )
        return QueryRef(**query_ref) if query_ref else None

    def get_query_response_refs(
        self, skip: int, limit: int, order: str, org_id: str
    ) -> list[QueryRef]:
        query_refs = (
            MongoDB.find(QUERY_RESPONSE_REF_COL, {"organization_id": ObjectId(org_id)})
            .sort([(order, DESCENDING)])
            .skip(skip)
            .limit(limit)
        )
        return [QueryRef(**qrr) for qrr in query_refs]

    def update_last_updated(
        self, query_id: str, updated_query_response_ref: dict
    ) -> str:
        return MongoDB.update_one(
            QUERY_RESPONSE_REF_COL,
            {"query_response_id": ObjectId(query_id)},
            updated_query_response_ref,
        )

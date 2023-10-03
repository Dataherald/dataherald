from bson import ObjectId

from config import QUERY_RESPONSE_COL, QUERY_RESPONSE_REF_COL, QUESTION_COL
from database.mongo import DESCENDING, MongoDB
from modules.query.models.entities import QueryRef, Question
from modules.query.models.responses import CoreQueryResponse
from utils.misc import get_next_display_id


class QueryRepository:
    def get_question(self, question_id: str) -> Question:
        question = MongoDB.find_by_id(QUESTION_COL, ObjectId(question_id))
        return Question(**question) if question else None

    def get_questions(self, question_ids: list[str]) -> list[Question]:
        object_ids = [ObjectId(id) for id in question_ids]
        questions = MongoDB.find_by_object_ids(QUESTION_COL, object_ids)
        return [Question(**q) for q in questions]

    def get_query_response(self, query_id: str) -> CoreQueryResponse:
        query_response = MongoDB.find_by_object_id(
            QUERY_RESPONSE_COL, ObjectId(query_id)
        )
        return CoreQueryResponse(**query_response) if query_response else None

    def get_query_responses(self, query_ids: list[str]) -> list[CoreQueryResponse]:
        object_ids = [ObjectId(id) for id in query_ids]
        response_query = {"_id": {"$in": object_ids}}
        query_responses = MongoDB.find(QUERY_RESPONSE_COL, response_query)
        return [CoreQueryResponse(**qr) for qr in query_responses]

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

    def add_query_response_ref(
        self,
        query_response_ref_data: dict,
    ) -> str:
        str(MongoDB.insert_one(QUERY_RESPONSE_REF_COL, query_response_ref_data))

    def update_query_response_ref(
        self, query_id: str, new_query_response_ref_data: dict
    ) -> int:
        return MongoDB.update_one(
            QUERY_RESPONSE_REF_COL,
            {"query_response_id": ObjectId(query_id)},
            new_query_response_ref_data,
        )

    def get_next_display_id(self, org_id: str) -> str:
        return get_next_display_id(QUERY_RESPONSE_REF_COL, ObjectId(org_id), "QR")

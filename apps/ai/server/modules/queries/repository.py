from bson.objectid import ObjectId

from config import QUERY_RESPONSE_COL, QUERY_RESPONSE_REF_COL, QUESTION_COL
from database.mongo import MongoDB
from modules.queries.models.entities import Query, QueryRef, Question


class QueriesRepository:
    def get_question(self, query_id: ObjectId) -> Question:
        return Question(**MongoDB.find_by_object_id(QUESTION_COL, query_id))

    def get_questions(self, query_ids: list[ObjectId]) -> list[Question]:
        questions = MongoDB.find_by_object_ids(QUESTION_COL, query_ids)
        return [Question(**q) for q in questions]

    def get_query_response(self, query_id: ObjectId) -> Query:
        return Query(**MongoDB.find_by_object_id(QUERY_RESPONSE_COL, query_id))

    def get_query_response_ref(self, query_id: ObjectId) -> QueryRef:
        return QueryRef(
            **MongoDB.find_one(QUERY_RESPONSE_REF_COL, {"query_response_id": query_id})
        )

    def get_query_response_refs(self, skip, limit) -> list[QueryRef]:
        query_refs = MongoDB.find(QUERY_RESPONSE_REF_COL, {}).skip(skip).limit(limit)
        return [QueryRef(**qrr) for qrr in query_refs]

    def get_query_responses(self, object_ids) -> list[Query]:
        response_query = {"_id": {"$in": object_ids}}
        query_responses = MongoDB.find(QUERY_RESPONSE_COL, response_query)
        return [Query(**qr) for qr in query_responses]

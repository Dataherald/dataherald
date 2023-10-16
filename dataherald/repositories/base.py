from bson.objectid import ObjectId
from pymongo import DESCENDING

from dataherald.types import Response

DB_COLLECTION = "responses"


class ResponseRepository:
    def __init__(self, storage):
        self.storage = storage

    def insert(self, response: Response) -> Response:
        response_dict = response.dict(exclude={"id"})
        response_dict["question_id"] = ObjectId(response.question_id)
        response.id = str(self.storage.insert_one(DB_COLLECTION, response_dict))
        return response

    def find_one(self, query: dict) -> Response | None:
        row = self.storage.find_one(DB_COLLECTION, query)
        if not row:
            return None
        row["id"] = str(row["_id"])
        row["question_id"] = str(row["question_id"])
        return Response(**row)

    def update(self, response: Response) -> Response:
        response_dict = response.dict(exclude={"id"})
        response_dict["question_id"] = ObjectId(response.question_id)

        self.storage.update_or_create(
            DB_COLLECTION,
            {"_id": ObjectId(response.id)},
            response_dict,
        )
        return response

    def find_by_id(self, id: str) -> Response | None:
        row = self.storage.find_one(DB_COLLECTION, {"_id": ObjectId(id)})
        if not row:
            return None
        row["id"] = str(row["_id"])
        row["question_id"] = str(row["question_id"])
        return Response(**row)

    def find_by(self, query: dict, page: int = 1, limit: int = 10) -> list[Response]:
        rows = self.storage.find(
            DB_COLLECTION,
            query,
            page=page,
            limit=limit,
            sort=[("created_at", DESCENDING)],
        )
        result = []
        for row in rows:
            row["id"] = str(row["_id"])
            row["question_id"] = str(row["question_id"])
            result.append(Response(**row))
        return result

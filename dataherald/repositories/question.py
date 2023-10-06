from bson.objectid import ObjectId

from dataherald.types import Question

DB_COLLECTION = "questions"


class QuestionRepository:
    def __init__(self, storage):
        self.storage = storage

    def insert(self, question: Question) -> Question:
        question_dict = question.dict(exclude={"id"})
        question_dict["db_connection_id"] = ObjectId(question.db_connection_id)
        question.id = str(self.storage.insert_one(DB_COLLECTION, question_dict))
        return question

    def find_one(self, query: dict) -> Question | None:
        row = self.storage.find_one(DB_COLLECTION, query)
        if not row:
            return None
        row["id"] = str(row["_id"])
        row["db_connection_id"] = str(row["db_connection_id"])
        return Question(**row)

    def find_by_id(self, id: str) -> Question | None:
        row = self.storage.find_one(DB_COLLECTION, {"_id": ObjectId(id)})
        if not row:
            return None
        row["id"] = str(row["_id"])
        row["db_connection_id"] = str(row["db_connection_id"])
        return Question(**row)

    def find_by(self, query: dict, page: int = 1, limit: int = 10) -> list[Question]:
        rows = self.storage.find(DB_COLLECTION, query, page=page, limit=limit)
        result = []
        for row in rows:
            row["id"] = str(row["_id"])
            row["db_connection_id"] = str(row["db_connection_id"])
            result.append(Question(**row))
        return result

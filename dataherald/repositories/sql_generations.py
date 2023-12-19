from bson.objectid import ObjectId

from dataherald.types import SQLGeneration

DB_COLLECTION = "sql_generations"


class SQLGenerationNotFoundError(Exception):
    pass


class SQLGenerationRepository:
    def __init__(self, storage):
        self.storage = storage

    def insert(self, sql_generation: SQLGeneration) -> SQLGeneration:
        sql_generation_dict = sql_generation.dict(exclude={"id"})
        sql_generation_dict["prompt_id"] = str(sql_generation.prompt_id)
        sql_generation.id = str(
            self.storage.insert_one(DB_COLLECTION, sql_generation_dict)
        )
        return sql_generation

    def update(self, sql_generation: SQLGeneration) -> SQLGeneration:
        sql_generation_dict = sql_generation.dict(exclude={"id"})
        sql_generation_dict["prompt_id"] = str(sql_generation.prompt_id)
        self.storage.update_or_create(
            DB_COLLECTION,
            {"_id": ObjectId(sql_generation.id)},
            sql_generation_dict,
        )
        return sql_generation

    def find_one(self, query: dict) -> SQLGeneration | None:
        row = self.storage.find_one(DB_COLLECTION, query)
        if not row:
            return None
        row["id"] = str(row["_id"])
        return SQLGeneration(**row)

    def find_by_id(self, id: str) -> SQLGeneration | None:
        row = self.storage.find_one(DB_COLLECTION, {"_id": ObjectId(id)})
        if not row:
            return None
        row["id"] = str(row["_id"])
        return SQLGeneration(**row)

    def find_by(
        self, query: dict, page: int = 1, limit: int = 10
    ) -> list[SQLGeneration]:
        rows = self.storage.find(DB_COLLECTION, query, page=page, limit=limit)
        result = []
        for row in rows:
            row["id"] = str(row["_id"])
            result.append(SQLGeneration(**row))
        return result

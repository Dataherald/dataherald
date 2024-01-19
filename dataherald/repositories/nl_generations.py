from bson.objectid import ObjectId

from dataherald.types import NLGeneration

DB_COLLECTION = "nl_generations"


class NLGenerationNotFoundError(Exception):
    pass


class NLGenerationRepository:
    def __init__(self, storage):
        self.storage = storage

    def insert(self, nl_generation: NLGeneration) -> NLGeneration:
        nl_generation_dict = nl_generation.dict(exclude={"id"})
        nl_generation_dict["sql_generation_id"] = str(nl_generation.sql_generation_id)
        nl_generation.id = str(
            self.storage.insert_one(DB_COLLECTION, nl_generation_dict)
        )
        return nl_generation

    def update(self, nl_generation: NLGeneration) -> NLGeneration:
        nl_generation_dict = nl_generation.dict(exclude={"id"})
        nl_generation_dict["sql_generation_id"] = str(nl_generation.sql_generation_id)
        self.storage.update_or_create(
            DB_COLLECTION,
            {"_id": ObjectId(nl_generation.id)},
            nl_generation_dict,
        )
        return nl_generation

    def find_one(self, query: dict) -> NLGeneration | None:
        row = self.storage.find_one(DB_COLLECTION, query)
        if not row:
            return None
        row["id"] = str(row["_id"])
        return NLGeneration(**row)

    def find_by_id(self, id: str) -> NLGeneration | None:
        row = self.storage.find_one(DB_COLLECTION, {"_id": ObjectId(id)})
        if not row:
            return None
        row["id"] = str(row["_id"])
        return NLGeneration(**row)

    def find_by(self, query: dict, page: int = 0, limit: int = 0) -> list[NLGeneration]:
        if page > 0 and limit > 0:
            rows = self.storage.find(DB_COLLECTION, query, page=page, limit=limit)
        else:
            rows = self.storage.find(DB_COLLECTION, query)
        result = []
        for row in rows:
            row["id"] = str(row["_id"])
            result.append(NLGeneration(**row))
        return result

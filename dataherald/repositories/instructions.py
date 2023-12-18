from bson.objectid import ObjectId

from dataherald.types import Instruction

DB_COLLECTION = "instructions"


class InstructionRepository:
    def __init__(self, storage):
        self.storage = storage

    def insert(self, instruction: Instruction) -> Instruction:
        instruction_dict = instruction.dict(exclude={"id"})
        instruction_dict["db_connection_id"] = str(instruction.db_connection_id)
        instruction.id = str(self.storage.insert_one(DB_COLLECTION, instruction_dict))

        return instruction

    def find_one(self, query: dict) -> Instruction | None:
        row = self.storage.find_one(DB_COLLECTION, query)
        if not row:
            return None
        row["id"] = str(row["_id"])
        row["db_connection_id"] = str(row["db_connection_id"])
        return Instruction(**row)

    def update(self, instruction: Instruction) -> Instruction:
        instruction_dict = instruction.dict(exclude={"id"})
        instruction_dict["db_connection_id"] = str(instruction.db_connection_id)

        self.storage.update_or_create(
            DB_COLLECTION,
            {"_id": ObjectId(instruction.id)},
            instruction_dict,
        )
        return instruction

    def find_by_id(self, id: str) -> Instruction | None:
        row = self.storage.find_one(DB_COLLECTION, {"_id": ObjectId(id)})
        if not row:
            return None
        row["id"] = str(row["_id"])
        row["db_connection_id"] = str(row["db_connection_id"])
        return Instruction(**row)

    def find_by(self, query: dict, page: int = 1, limit: int = 10) -> list[Instruction]:
        rows = self.storage.find(DB_COLLECTION, query, page=page, limit=limit)
        result = []
        for row in rows:
            row["id"] = str(row["_id"])
            row["db_connection_id"] = str(row["db_connection_id"])
            result.append(Instruction(**row))
        return result

    def find_all(self, page: int = 0, limit: int = 0) -> list[Instruction]:
        rows = self.storage.find_all(DB_COLLECTION, page=page, limit=limit)
        result = []
        for row in rows:
            row["id"] = str(row["_id"])
            row["db_connection_id"] = str(row["db_connection_id"])
            result.append(Instruction(**row))
        return result

    def delete_by_id(self, id: str) -> int:
        return self.storage.delete_by_id(DB_COLLECTION, id)

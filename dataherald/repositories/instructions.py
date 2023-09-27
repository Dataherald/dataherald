from bson.objectid import ObjectId

from dataherald.types import Instruction

DB_COLLECTION = "instructions"


class InstructionRepository:
    def __init__(self, storage):
        self.storage = storage

    def insert(self, instruction: Instruction) -> Instruction:
        instruction.id = str(
            self.storage.insert_one(DB_COLLECTION, instruction.dict(exclude={"id"}))
        )
        return instruction

    def find_one(self, query: dict) -> Instruction | None:
        row = self.storage.find_one(DB_COLLECTION, query)
        if not row:
            return None
        return Instruction(**row)

    def update(self, instruction: Instruction) -> Instruction:
        self.storage.update_or_create(
            DB_COLLECTION,
            {"_id": ObjectId(instruction.id)},
            instruction.dict(exclude={"id"}),
        )
        return instruction

    def find_by_id(self, id: str) -> Instruction | None:
        row = self.storage.find_one(DB_COLLECTION, {"_id": ObjectId(id)})
        if not row:
            return None
        return Instruction(**row)

    def find_by(self, query: dict) -> list[Instruction]:
        rows = self.storage.find(DB_COLLECTION, query)
        result = []
        for row in rows:
            obj = Instruction(**row)
            obj.id = str(row["_id"])
            result.append(obj)
        return result

    def find_all(self) -> list[Instruction]:
        rows = self.storage.find_all(DB_COLLECTION)
        return [Instruction(id=str(row["_id"]), **row) for row in rows]

    def delete_by_id(self, id: str) -> int:
        return self.storage.delete_by_id(DB_COLLECTION, id)

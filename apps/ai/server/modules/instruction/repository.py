from bson import ObjectId

from config import INSTRUCTION_COL
from database.mongo import MongoDB
from modules.instruction.models.entities import Instruction


class InstructionRepository:
    def get_instruction(self, instruction_id: str, org_id: str) -> Instruction:
        instruction = MongoDB.find_one(
            INSTRUCTION_COL,
            {
                "_id": ObjectId(instruction_id),
                "metadata.dh_internal.organization_id": org_id,
            },
        )
        return (
            Instruction(id=str(instruction["_id"]), **instruction)
            if instruction
            else None
        )

    def get_instructions(self, db_connection_id: str, org_id: str) -> list[Instruction]:
        instructions = MongoDB.find(
            INSTRUCTION_COL,
            {
                "db_connection_id": db_connection_id,
                "metadata.dh_internal.organization_id": org_id,
            },
        )

        return [
            Instruction(id=str(instruction["_id"]), **instruction)
            for instruction in instructions
        ]

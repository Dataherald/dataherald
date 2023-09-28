from modules.instruction.models.entities import BaseInstruction


class InstructionResponse(BaseInstruction):
    id: str
    db_connection_id: str

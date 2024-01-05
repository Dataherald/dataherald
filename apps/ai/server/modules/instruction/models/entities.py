from datetime import datetime

from pydantic import BaseModel, Extra


class BaseInstruction(BaseModel):
    instruction: str
    db_connection_id: str | None


class DHInstructionMetadata(BaseModel):
    organization_id: str | None


class InstructionMetadata(BaseModel):
    dh_internal: DHInstructionMetadata | None

    class Config:
        extra = Extra.allow


class Instruction(BaseInstruction):
    id: str
    created_at: datetime | None
    metadata: InstructionMetadata | None

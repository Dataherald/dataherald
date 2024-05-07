from datetime import datetime

from pydantic import BaseModel, Extra

from utils.validation import ObjectIdString


class BaseInstruction(BaseModel):
    instruction: str
    db_connection_id: ObjectIdString | None


class DHInstructionMetadata(BaseModel):
    organization_id: ObjectIdString | None


class InstructionMetadata(BaseModel):
    dh_internal: DHInstructionMetadata | None

    class Config:
        extra = Extra.allow


class Instruction(BaseInstruction):
    id: ObjectIdString | None
    created_at: datetime | None
    metadata: InstructionMetadata | None


class AggrInstruction(Instruction):
    db_connection_alias: str | None

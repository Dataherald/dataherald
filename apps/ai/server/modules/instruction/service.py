import httpx

from config import settings
from exceptions.exception_handlers import raise_engine_exception
from modules.db_connection.service import DBConnectionService
from modules.instruction.models.entities import (
    DHInstructionMetadata,
    Instruction,
    InstructionMetadata,
)
from modules.instruction.models.exceptions import (
    InstructionNotFoundError,
    SingleInstructionOnlyError,
)
from modules.instruction.models.requests import InstructionRequest
from modules.instruction.models.responses import AggrInstruction
from modules.instruction.repository import InstructionRepository
from utils.misc import reserved_key_in_metadata


class InstructionService:
    def __init__(self):
        self.repo = InstructionRepository()
        self.db_connection_service = DBConnectionService()

    def get_instructions(
        self, org_id: str, db_connection_id: str = None
    ) -> list[AggrInstruction]:
        instructions = []
        if db_connection_id:
            db_connections = [
                self.db_connection_service.get_db_connection(db_connection_id, org_id)
            ]
        else:
            db_connections = self.db_connection_service.get_db_connections(org_id)

        for db_connection in db_connections:
            instructions += [
                AggrInstruction(
                    **instruction.dict(), db_connection_alias=db_connection.alias
                )
                for instruction in self.repo.get_instructions(db_connection.id, org_id)
            ]
        return instructions

    def get_instruction(self, instruction_id: str, org_id: str) -> AggrInstruction:
        instruction = self.get_instruction_in_org(instruction_id, org_id)
        return AggrInstruction(
            **instruction.dict(),
            db_connection_alias=self.db_connection_service.get_db_connection_in_org(
                instruction.db_connection_id, org_id
            ).alias,
        )

    def get_first_instruction(
        self, db_connection_id: str, org_id: str
    ) -> AggrInstruction:
        db_connection = self.db_connection_service.get_db_connection_in_org(
            db_connection_id, org_id
        )
        instructions = self.repo.get_instructions(db_connection_id, org_id)
        if len(instructions) == 0:
            raise InstructionNotFoundError(org_id, db_connection_id=db_connection_id)
        return AggrInstruction(
            **instructions[0].dict(), db_connection_alias=db_connection.alias
        )

    async def add_instruction(
        self, instruction_request: InstructionRequest, org_id: str
    ) -> AggrInstruction:
        reserved_key_in_metadata(instruction_request.metadata)

        if self.repo.get_instructions(instruction_request.db_connection_id, org_id):
            raise SingleInstructionOnlyError(
                instruction_request.db_connection_id, org_id
            )

        db_connection = self.db_connection_service.get_db_connection_in_org(
            instruction_request.db_connection_id, org_id
        )

        instruction_request.metadata = InstructionMetadata(
            dh_internal=DHInstructionMetadata(organization_id=org_id)
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url + "/instructions",
                json=instruction_request.dict(exclude_unset=True),
            )
            raise_engine_exception(response, org_id=org_id)
            return AggrInstruction(
                **response.json(), db_connection_alias=db_connection.alias
            )

    async def update_instruction(
        self,
        instruction_id: str,
        instruction_request: InstructionRequest,
        org_id: str,
    ) -> AggrInstruction:
        reserved_key_in_metadata(instruction_request.metadata)
        instruction = self.get_instruction_in_org(instruction_id, org_id)

        if not instruction_request.db_connection_id:
            instruction_request.db_connection_id = instruction.db_connection_id

        db_connection = self.db_connection_service.get_db_connection_in_org(
            instruction_request.db_connection_id, org_id
        )

        instruction_request.metadata = InstructionMetadata(
            **instruction_request.metadata,
            dh_internal=DHInstructionMetadata(organization_id=org_id),
        )

        async with httpx.AsyncClient() as client:
            response = await client.put(
                settings.engine_url + f"/instructions/{instruction_id}",
                json=instruction_request.dict(exclude_unset=True),
            )
            raise_engine_exception(response, org_id=org_id)
            return AggrInstruction(
                **response.json(), db_connection_alias=db_connection.alias
            )

    async def delete_instruction(self, instruction_id: str, org_id: str):
        instruction = self.get_instruction_in_org(instruction_id, org_id)
        self.db_connection_service.get_db_connection_in_org(
            instruction.db_connection_id, org_id
        )

        async with httpx.AsyncClient() as client:
            response = await client.delete(
                settings.engine_url + f"/instructions/{instruction_id}",
            )
            raise_engine_exception(response, org_id=org_id)
            return {"id": instruction_id}

    def get_instruction_in_org(self, instruction_id: str, org_id: str) -> Instruction:
        instruction = self.repo.get_instruction(instruction_id, org_id)
        if not instruction:
            raise InstructionNotFoundError(org_id, instruction_id=instruction_id)
        return instruction

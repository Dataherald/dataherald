import httpx
from fastapi import HTTPException, status

from config import settings
from modules.db_connection.service import DBConnectionService
from modules.instruction.models.entities import (
    DHInstructionMetadata,
    Instruction,
    InstructionMetadata,
)
from modules.instruction.models.requests import InstructionRequest
from modules.instruction.models.responses import InstructionResponse
from modules.instruction.repository import InstructionRepository
from modules.organization.service import OrganizationService
from utils.exception import raise_for_status
from utils.misc import reserved_key_in_metadata


class InstructionService:
    def __init__(self):
        self.repo = InstructionRepository()
        self.org_service = OrganizationService()
        self.db_connection_service = DBConnectionService()

    def get_instructions(
        self, db_connection_id: str, org_id: str
    ) -> list[InstructionResponse]:
        db_connection = self.db_connection_service.get_db_connection(
            db_connection_id, org_id
        )

        if not db_connection:
            return []

        return self.repo.get_instructions(db_connection_id, org_id)

    def get_instruction(self, instruction_id: str, org_id: str) -> InstructionResponse:
        return self.get_instruction_in_org(instruction_id, org_id)

    def get_first_instruction(self, org_id: str) -> InstructionResponse:
        organization = self.org_service.get_organization(org_id)
        instructions = self.repo.get_instructions(organization.db_connection_id, org_id)
        if len(instructions) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Instruction not found",
            )
        return instructions[0]

    async def add_instruction(
        self, instruction_request: InstructionRequest, org_id: str
    ) -> InstructionResponse:
        reserved_key_in_metadata(instruction_request.metadata)

        if not instruction_request.db_connection_id:
            instruction_request.db_connection_id = self.org_service.get_organization(
                org_id
            ).db_connection_id

        self.db_connection_service.get_db_connection_in_org(
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
            raise_for_status(response.status_code, response.text)
            return InstructionResponse(**response.json())

    async def update_instruction(
        self,
        instruction_id: str,
        instruction_request: InstructionRequest,
        org_id: str,
    ) -> InstructionResponse:
        reserved_key_in_metadata(instruction_request.metadata)
        instruction = self.get_instruction_in_org(instruction_id, org_id)

        if not instruction_request.db_connection_id:
            instruction_request.db_connection_id = instruction.db_connection_id

        self.db_connection_service.get_db_connection_in_org(
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
            raise_for_status(response.status_code, response.text)
            return InstructionResponse(**response.json())

    async def delete_instruction(self, instruction_id: str, org_id: str):
        instruction = self.get_instruction_in_org(instruction_id, org_id)
        self.db_connection_service.get_db_connection_in_org(
            instruction.db_connection_id, org_id
        )

        async with httpx.AsyncClient() as client:
            response = await client.delete(
                settings.engine_url + f"/instructions/{instruction_id}",
            )
            raise_for_status(response.status_code, response.text)
            return {"id": instruction_id}

    def get_instruction_in_org(self, instruction_id: str, org_id: str) -> Instruction:
        instruction = self.repo.get_instruction(instruction_id, org_id)
        if not instruction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Instruction not found",
            )
        return instruction

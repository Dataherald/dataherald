import httpx

from config import settings
from modules.instruction.models.requests import InstructionRequest
from modules.instruction.models.responses import InstructionResponse
from utils.exception import raise_for_status


class InstructionService:
    async def get_instructions(
        self, db_connection_id: str
    ) -> list[InstructionResponse]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                settings.k2_core_url + "/instructions",
                params={"db_connection_id": db_connection_id},
            )
            raise_for_status(response.status_code, response.text)
            return [InstructionResponse(**td) for td in response.json()]

    async def add_instruction(
        self, instruction_request: InstructionRequest, db_connection_id: str
    ) -> InstructionResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.k2_core_url + "/instructions",
                json={
                    "db_connection_id": db_connection_id,
                    **instruction_request.dict(),
                },
            )
            raise_for_status(response.status_code, response.text)
            return InstructionResponse(**response.json())

    async def update_instruction(
        self,
        instruction_id,
        instruction_request: InstructionRequest,
        db_connection_id: str,
    ) -> InstructionResponse:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                settings.k2_core_url + f"/instructions/{instruction_id}",
                json={
                    "db_connection_id": db_connection_id,
                    **instruction_request.dict(),
                },
            )
            raise_for_status(response.status_code, response.text)
            return InstructionResponse(**response.json())

    async def delete_instruction(self, instruction_id):
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                settings.k2_core_url + f"/instructions/{instruction_id}",
            )
            raise_for_status(response.status_code, response.text)
            return {"id": instruction_id}

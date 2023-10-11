from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from modules.instruction.models.requests import InstructionRequest
from modules.instruction.models.responses import InstructionResponse
from modules.instruction.service import InstructionService
from utils.auth import Authorize, VerifyToken

router = APIRouter(
    prefix="/instruction",
    responses={404: {"description": "Not found"}},
)

token_auth_scheme = HTTPBearer()
authorize = Authorize()
table_description_service = InstructionService()


@router.get("/list")
async def get_instructions(
    token: str = Depends(token_auth_scheme),
) -> list[InstructionResponse]:
    user = authorize.user(VerifyToken(token.credentials).verify())
    organization = authorize.get_organization_by_user_response(user)
    return await table_description_service.get_instructions(
        organization.db_connection_id
    )


@router.get("")
async def get_instruction(
    token: str = Depends(token_auth_scheme),
) -> InstructionResponse:
    user = authorize.user(VerifyToken(token.credentials).verify())
    organization = authorize.get_organization_by_user_response(user)
    return await table_description_service.get_instruction(
        organization.db_connection_id
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_instructions(
    instruction_request: InstructionRequest,
    token: str = Depends(token_auth_scheme),
) -> InstructionResponse:
    user = authorize.user(VerifyToken(token.credentials).verify())
    organization = authorize.get_organization_by_user_response(user)
    return await table_description_service.add_instruction(
        instruction_request, organization.db_connection_id
    )


@router.put("/{id}")
async def update_instruction(
    id: str,
    instruction_request: InstructionRequest,
    token: str = Depends(token_auth_scheme),
) -> InstructionResponse:
    user = authorize.user(VerifyToken(token.credentials).verify())
    organization = authorize.get_organization_by_user_response(user)
    authorize.instruction_in_organization(id, organization)
    return await table_description_service.update_instruction(
        id, instruction_request, organization.db_connection_id
    )


@router.delete("/{id}")
async def delete_instruction(
    id: str,
    token: str = Depends(token_auth_scheme),
):
    user = authorize.user(VerifyToken(token.credentials).verify())
    organization = authorize.get_organization_by_user_response(user)
    authorize.instruction_in_organization(id, organization)
    return await table_description_service.delete_instruction(id)

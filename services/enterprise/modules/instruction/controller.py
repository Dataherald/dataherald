from fastapi import APIRouter, Security, status

from modules.instruction.models.requests import InstructionRequest
from modules.instruction.models.responses import (
    ACInstructionResponse,
    InstructionResponse,
)
from modules.instruction.service import InstructionService
from utils.auth import Authorize, User, authenticate_user, get_api_key
from utils.validation import ObjectIdString

router = APIRouter(
    prefix="/api/instructions",
    responses={404: {"description": "Not found"}},
)

ac_router = APIRouter(
    prefix="/instructions",
    responses={404: {"description": "Not found"}},
)

authorize = Authorize()
instruction_service = InstructionService()


@router.get("")
async def get_instructions(
    db_connection_id: ObjectIdString = None,
    api_key: str = Security(get_api_key),
) -> list[InstructionResponse]:
    org_id = api_key.organization_id
    return instruction_service.get_instructions(org_id, db_connection_id)


@router.get("/{id}")
async def get_instruction(
    id: ObjectIdString, api_key: str = Security(get_api_key)
) -> InstructionResponse:
    org_id = api_key.organization_id
    return instruction_service.get_instruction(id, org_id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_instructions(
    instruction_request: InstructionRequest,
    api_key: str = Security(get_api_key),
) -> InstructionResponse:
    return await instruction_service.add_instruction(
        instruction_request, api_key.organization_id
    )


@router.put("/{id}")
async def update_instruction(
    id: ObjectIdString,
    instruction_request: InstructionRequest,
    api_key: str = Security(get_api_key),
) -> InstructionResponse:
    return await instruction_service.update_instruction(
        id, instruction_request, api_key.organization_id
    )


@router.delete("/{id}")
async def delete_instruction(
    id: ObjectIdString,
    api_key: str = Security(get_api_key),
):
    return await instruction_service.delete_instruction(id, api_key.organization_id)


@ac_router.get("")
async def ac_get_instructions(
    db_connection_id: ObjectIdString = None,
    user: User = Security(authenticate_user),
) -> list[ACInstructionResponse]:
    return instruction_service.get_instructions(user.organization_id, db_connection_id)


@ac_router.get("/first")
async def ac_get_first_instruction(
    db_connection_id: ObjectIdString,
    user: User = Security(authenticate_user),
) -> ACInstructionResponse:
    return instruction_service.get_first_instruction(
        db_connection_id, user.organization_id
    )


@ac_router.get("/{id}")
async def ac_get_instruction(
    id: ObjectIdString,
    user: User = Security(authenticate_user),
) -> ACInstructionResponse:
    return instruction_service.get_instruction(id, user.organization_id)


@ac_router.post("", status_code=status.HTTP_201_CREATED)
async def ac_add_instructions(
    instruction_request: InstructionRequest,
    user: User = Security(authenticate_user),
) -> ACInstructionResponse:
    return await instruction_service.add_instruction(
        instruction_request, user.organization_id
    )


@ac_router.put("/{id}")
async def ac_update_instruction(
    id: ObjectIdString,
    instruction_request: InstructionRequest,
    user: User = Security(authenticate_user),
) -> ACInstructionResponse:
    return await instruction_service.update_instruction(
        id, instruction_request, user.organization_id
    )


@ac_router.delete("/{id}")
async def ac_delete_instruction(
    id: ObjectIdString,
    user: User = Security(authenticate_user),
):
    return await instruction_service.delete_instruction(id, user.organization_id)

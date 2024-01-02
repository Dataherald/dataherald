from fastapi import APIRouter, Depends, Security, status
from fastapi.security import HTTPBearer

from modules.generation.aggr_service import AggrgationGenerationService
from modules.generation.models.requests import (
    GenerationUpdateRequest,
    SlackGenerationRequest,
    SQLGenerationExecuteRequest,
    SQLRequest,
)
from modules.generation.models.responses import (
    GenerationListResponse,
    GenerationResponse,
    GenerationSlackResponse,
    NLGenerationResponse,
)
from modules.organization.service import OrganizationService
from utils.auth import Authorize, VerifyToken, get_api_key

router = APIRouter(
    prefix="/generations",
    responses={404: {"description": "Not found"}},
)

api_router = APIRouter(
    prefix="/api/generations",
    responses={404: {"description": "Not found"}},
)

token_auth_scheme = HTTPBearer()
authorize = Authorize()
generation_service = AggrgationGenerationService()
org_service = OrganizationService()


@router.get("")
async def get_generations(
    page: int = 0,
    page_size: int = 20,
    order: str = "created_at",
    ascend: bool = False,
    token: str = Depends(token_auth_scheme),
) -> list[GenerationListResponse]:
    org_id = authorize.user(VerifyToken(token.credentials).verify()).organization_id
    return generation_service.get_generation_list(
        page=page,
        page_size=page_size,
        order=order,
        ascend=ascend,
        org_id=org_id,
    )


@api_router.get("")
async def api_get_generations(
    page: int = 0,
    page_size: int = 20,
    order: str = "created_at",
    ascend: bool = True,
    api_key: str = Security(get_api_key),
) -> list[GenerationListResponse]:
    return generation_service.get_generation_list(
        page=page,
        page_size=page_size,
        order=order,
        ascend=ascend,
        org_id=api_key.organization_id,
    )


@router.get("/{id}")
async def get_generation(
    id: str, token: str = Depends(token_auth_scheme)
) -> GenerationResponse:
    org_id = authorize.user(VerifyToken(token.credentials).verify()).organization_id
    return await generation_service.get_generation(id, org_id)


@api_router.get("/{id}")
async def api_get_generation(
    id: str, api_key: str = Security(get_api_key)
) -> GenerationResponse:
    return generation_service.get_generation(id, api_key.organization_id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_generation(
    generation_request: SlackGenerationRequest,
    token: str = Depends(token_auth_scheme),
) -> GenerationSlackResponse:
    VerifyToken(token.credentials)
    organization = org_service.get_organization_by_slack_workspace_id(
        generation_request.slack_info.workspace_id
    )
    return await generation_service.create_generation(generation_request, organization)


@router.put("/{id}")
async def update_generation(
    id: str,
    generation_request: GenerationUpdateRequest,
    token: str = Depends(token_auth_scheme),
) -> GenerationResponse:
    user = authorize.user(VerifyToken(token.credentials).verify())
    return await generation_service.update_generation(
        id, generation_request, user.organization_id, user
    )


# playground endpoint
@router.post("/prompts/sql-generations", status_code=status.HTTP_201_CREATED)
async def create_prompt_sql_generation_result(
    request: SQLGenerationExecuteRequest,
    token: str = Depends(token_auth_scheme),
) -> GenerationResponse:
    user = authorize.user(VerifyToken(token.credentials).verify())
    return await generation_service.create_prompt_sql_generation_result(
        request, user.organization_id, playground=True
    )


@router.post("/{id}/sql-generations", status_code=status.HTTP_201_CREATED)
async def create_sql_generation_result(
    id: str,
    sql_result_request: SQLRequest,
    token: str = Depends(token_auth_scheme),
) -> GenerationResponse:
    user = authorize.user(VerifyToken(token.credentials).verify())
    return await generation_service.create_sql_generation_result(
        id, sql_result_request, user.organization_id, user
    )


@router.post("/{id}/nl-generations")
async def create_message(
    id: str, token: str = Depends(token_auth_scheme)
) -> NLGenerationResponse:
    user = authorize.user(VerifyToken(token.credentials).verify())
    return await generation_service.create_nl_generation(id, user.organization_id)


@router.post("/{id}/messages")
async def send_message(id: str, token: str = Depends(token_auth_scheme)):
    user = authorize.user(VerifyToken(token.credentials).verify())
    return await generation_service.send_message(id, user.organization_id)


@router.post("/{id}", status_code=status.HTTP_201_CREATED)
async def create_sql_nl_generation(
    id: str,
    token: str = Depends(token_auth_scheme),
) -> GenerationResponse:
    user = authorize.user(VerifyToken(token.credentials).verify())
    return await generation_service.create_sql_nl_generation(
        id, user.organization_id, user
    )

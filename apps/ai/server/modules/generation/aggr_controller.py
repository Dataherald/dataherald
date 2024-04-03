from fastapi import APIRouter, Security, status
from fastapi.responses import StreamingResponse

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
from modules.organization.invoice.models.entities import UsageType
from modules.organization.invoice.service import InvoiceService
from modules.organization.service import OrganizationService
from utils.auth import User, authenticate_user, get_api_key, verify_token
from utils.validation import ObjectIdString

router = APIRouter(
    prefix="/api/generations",
    responses={404: {"description": "Not found"}},
)

ac_router = APIRouter(
    prefix="/generations",
    responses={404: {"description": "Not found"}},
)

generation_service = AggrgationGenerationService()
org_service = OrganizationService()
invoice_service = InvoiceService()


@router.get("")
async def get_generations(
    page: int = 0,
    page_size: int = 20,
    order: str = "created_at",
    ascend: bool = True,
    search_term: str = "",
    db_connection_id: ObjectIdString = None,
    api_key: str = Security(get_api_key),
) -> list[GenerationListResponse]:
    return generation_service.get_generation_list(
        page=page,
        page_size=page_size,
        order=order,
        ascend=ascend,
        org_id=api_key.organization_id,
        search_term=search_term,
        db_connection_id=db_connection_id,
    )


@router.get("/{id}")
async def get_generation(
    id: ObjectIdString, api_key: str = Security(get_api_key)
) -> GenerationResponse:
    return await generation_service.get_generation(id, api_key.organization_id)


@ac_router.get("")
async def ac_get_generations(
    page: int = 0,
    page_size: int = 20,
    order: str = "created_at",
    ascend: bool = False,
    search_term: str = "",
    db_connection_id: ObjectIdString = None,
    user: User = Security(authenticate_user),
) -> list[GenerationListResponse]:
    return generation_service.get_generation_list(
        page=page,
        page_size=page_size,
        order=order,
        ascend=ascend,
        org_id=user.organization_id,
        search_term=search_term,
        db_connection_id=db_connection_id,
    )


@ac_router.get("/{id}")
async def ac_get_generation(
    id: ObjectIdString, user: User = Security(authenticate_user)
) -> GenerationResponse:
    return await generation_service.get_generation(id, user.organization_id)


# slack endpoint
@ac_router.post("", status_code=status.HTTP_201_CREATED)
async def ac_create_generation(
    generation_request: SlackGenerationRequest,
    token: dict = Security(verify_token),  # noqa: ARG001
) -> GenerationSlackResponse:
    organization = org_service.get_organization_by_slack_workspace_id(
        generation_request.slack_info.workspace_id
    )
    invoice_service.check_usage(
        organization.id, type=UsageType.SQL_GENERATION, quantity=1
    )
    response = await generation_service.create_generation(
        generation_request, organization
    )
    invoice_service.record_usage(
        organization.id,
        type=UsageType.SQL_GENERATION,
        quantity=1,
        description=f"from slackbot with prompt id {response.id}",
    )
    return response


@ac_router.put("/{id}")
async def ac_update_generation(
    id: ObjectIdString,
    generation_request: GenerationUpdateRequest,
    user: User = Security(authenticate_user),
) -> GenerationResponse:
    return await generation_service.update_generation(
        id, generation_request, user.organization_id, user
    )


@ac_router.post("/prompts/sql-generations/stream", status_code=status.HTTP_201_CREATED)
async def ac_create_prompt_sql_generation_stream(
    request: SQLGenerationExecuteRequest,
    user: User = Security(authenticate_user),
) -> StreamingResponse:
    invoice_service.check_usage(
        user.organization_id, type=UsageType.SQL_GENERATION, quantity=1
    )
    invoice_service.record_usage(
        user.organization_id,
        type=UsageType.SQL_GENERATION,
        quantity=1,
        description="from playground",
    )
    return StreamingResponse(
        generation_service.create_prompt_sql_generation_stream(
            request, user.organization_id, user.name
        )
    )


@ac_router.post("/{id}/sql-generations", status_code=status.HTTP_201_CREATED)
async def ac_create_sql_generation_result(
    id: ObjectIdString,
    sql_result_request: SQLRequest,
    user: User = Security(authenticate_user),
) -> GenerationResponse:
    return await generation_service.create_sql_generation_result(
        id, sql_result_request, user.organization_id, user
    )


@ac_router.post("/{id}/nl-generations")
async def ac_create_message(
    id: ObjectIdString, user: User = Security(authenticate_user)
) -> NLGenerationResponse:
    return await generation_service.create_nl_generation(id, user.organization_id)


@ac_router.post("/{id}/messages")
async def ac_send_message(id: ObjectIdString, user: User = Security(authenticate_user)):
    return await generation_service.send_message(id, user.organization_id)


@ac_router.post("/{id}", status_code=status.HTTP_201_CREATED)
async def ac_create_sql_nl_generation(
    id: ObjectIdString,
    user: User = Security(authenticate_user),
) -> GenerationResponse:
    invoice_service.check_usage(
        user.organization_id, type=UsageType.SQL_GENERATION, quantity=1
    )
    response = await generation_service.create_sql_nl_generation(
        id, user.organization_id, user
    )
    invoice_service.record_usage(
        user.organization_id,
        type=UsageType.SQL_GENERATION,
        quantity=1,
        description=f"from resubmit with prompt id {response.id}",
    )
    return response


@ac_router.get("/{id}/csv-file")
async def export_csv_file(
    id: ObjectIdString, user: User = Security(authenticate_user)
) -> StreamingResponse:
    return await generation_service.export_csv_file(id, user.organization_id)

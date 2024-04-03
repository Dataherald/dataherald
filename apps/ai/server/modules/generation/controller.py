from fastapi import APIRouter, Security, status
from fastapi.responses import StreamingResponse

from modules.generation.models.requests import (
    NLGenerationRequest,
    PromptRequest,
    PromptSQLGenerationRequest,
    PromptSQLNLGenerationRequest,
    SQLGenerationRequest,
    SQLNLGenerationRequest,
)
from modules.generation.models.responses import (
    NLGenerationResponse,
    PromptResponse,
    SQLGenerationResponse,
)
from modules.generation.service import GenerationService
from modules.organization.invoice.models.entities import UsageType
from modules.organization.invoice.service import InvoiceService
from utils.auth import get_api_key
from utils.validation import ObjectIdString

router = APIRouter(
    prefix="/api",
    responses={404: {"description": "Not found"}},
)

generation_service = GenerationService()
invoice_service = InvoiceService()


@router.post("/prompts", status_code=status.HTTP_201_CREATED)
async def create_prompt(
    prompt_request: PromptRequest,
    api_key: str = Security(get_api_key),
) -> PromptResponse:
    return await generation_service.create_prompt(
        prompt_request, api_key.organization_id
    )


@router.post("/prompts/sql-generations", status_code=status.HTTP_201_CREATED)
async def create_prompt_sql_generation(
    request: PromptSQLGenerationRequest,
    api_key: str = Security(get_api_key),
) -> SQLGenerationResponse:
    invoice_service.check_usage(
        api_key.organization_id, type=UsageType.SQL_GENERATION, quantity=1
    )
    response = await generation_service.create_prompt_sql_generation(
        request, api_key.organization_id
    )
    invoice_service.record_usage(
        api_key.organization_id,
        type=UsageType.SQL_GENERATION,
        quantity=1,
        description=f"from /api/prompts/sql-generation: {response.id}",
    )
    return response


@router.post("/prompts/sql-generations/stream", status_code=status.HTTP_201_CREATED)
async def create_prompt_sql_generation_stream(
    request: PromptSQLGenerationRequest,
    api_key: str = Security(get_api_key),
) -> StreamingResponse:
    invoice_service.check_usage(
        api_key.organization_id, type=UsageType.SQL_GENERATION, quantity=1
    )
    invoice_service.record_usage(
        api_key.organization_id,
        type=UsageType.SQL_GENERATION,
        quantity=1,
        description="from playground",
    )
    return StreamingResponse(
        generation_service.create_prompt_sql_generation_stream(
            request, api_key.organization_id
        )
    )


@router.post(
    "/prompts/sql-generations/nl-generations", status_code=status.HTTP_201_CREATED
)
async def create_prompt_sql_nl_generation(
    request: PromptSQLNLGenerationRequest,
    api_key: str = Security(get_api_key),
) -> NLGenerationResponse:
    invoice_service.check_usage(
        api_key.organization_id, type=UsageType.SQL_GENERATION, quantity=1
    )
    response = await generation_service.create_prompt_sql_nl_generation(
        request, api_key.organization_id
    )
    invoice_service.record_usage(
        api_key.organization_id,
        type=UsageType.SQL_GENERATION,
        quantity=1,
        description=f"from /api/prompts/sql-generations/nl-generations: {response.id}",
    )
    return response


@router.post("/prompts/{id}/sql-generations", status_code=status.HTTP_201_CREATED)
async def create_sql_generation(
    id: ObjectIdString,
    request: SQLGenerationRequest,
    api_key: str = Security(get_api_key),
) -> SQLGenerationResponse:
    invoice_service.check_usage(
        api_key.organization_id, type=UsageType.SQL_GENERATION, quantity=1
    )
    response = await generation_service.create_sql_generation(
        id, request, api_key.organization_id
    )
    invoice_service.record_usage(
        api_key.organization_id,
        type=UsageType.SQL_GENERATION,
        quantity=1,
        description=f"from /api/prompts/{id}/sql-generations: {response.id}",
    )
    return response


@router.post(
    "/prompts/{id}/sql-generations/nl-generations", status_code=status.HTTP_201_CREATED
)
async def create_sql_nl_generation(
    id: ObjectIdString,
    request: SQLNLGenerationRequest,
    api_key: str = Security(get_api_key),
) -> NLGenerationResponse:
    invoice_service.check_usage(
        api_key.organization_id, type=UsageType.SQL_GENERATION, quantity=1
    )
    response = await generation_service.create_sql_nl_generation(
        id, request, api_key.organization_id
    )
    invoice_service.record_usage(
        api_key.organization_id,
        type=UsageType.SQL_GENERATION,
        quantity=1,
        description=f"from /api/prompts/{id}/sql-generations/nl-generations: {response.id}",
    )
    return response


@router.post(
    "/sql-generations/{id}/nl-generations", status_code=status.HTTP_201_CREATED
)
async def create_nl_generation(
    id: ObjectIdString,
    request: NLGenerationRequest,
    api_key: str = Security(get_api_key),
) -> NLGenerationResponse:
    return await generation_service.create_nl_generation(
        id, request, api_key.organization_id
    )


@router.get("/prompts")
async def get_prompts(
    page: int = 0,
    page_size: int = 20,
    order: str = "created_at",
    ascend: bool = False,
    db_connection_id: str = None,
    api_key: str = Security(get_api_key),
) -> list[PromptResponse]:
    return generation_service.get_prompts(
        page,
        page_size,
        order,
        ascend,
        api_key.organization_id,
        db_connection_id=db_connection_id,
    )


@router.get("/prompts/{id}")
async def get_prompt(
    id: ObjectIdString,
    api_key: str = Security(get_api_key),
) -> PromptResponse:
    return generation_service.get_prompt(id, api_key.organization_id)


@router.get("/prompts/{id}/sql-generations")
async def get_sql_generations_by_prompt_id(
    id: ObjectIdString,
    page: int = 0,
    page_size: int = 20,
    order: str = "created_at",
    ascend: bool = False,
    api_key: str = Security(get_api_key),
):
    return generation_service.get_sql_generations(
        page, page_size, order, ascend, api_key.organization_id, id
    )


@router.get("/sql-generations")
async def get_sql_generations(
    page: int = 0,
    page_size: int = 20,
    order: str = "created_at",
    ascend: bool = False,
    api_key: str = Security(get_api_key),
) -> list[SQLGenerationResponse]:
    return generation_service.get_sql_generations(
        page, page_size, order, ascend, api_key.organization_id
    )


@router.get("/sql-generations/{id}")
async def get_sql_generation(
    id: ObjectIdString,
    api_key: str = Security(get_api_key),
) -> SQLGenerationResponse:
    return generation_service.get_sql_generation(id, api_key.organization_id)


@router.get("/sql-generations/{id}/nl-generations")
async def get_nl_generations_by_sql_generation_id(
    id: ObjectIdString,
    page: int = 0,
    page_size: int = 20,
    order: str = "created_at",
    ascend: bool = False,
    api_key: str = Security(get_api_key),
):
    return generation_service.get_nl_generations(
        page, page_size, order, ascend, api_key.organization_id, id
    )


@router.get("/nl-generations")
async def get_nl_generations(
    page: int = 0,
    page_size: int = 20,
    order: str = "created_at",
    ascend: bool = False,
    api_key: str = Security(get_api_key),
) -> list[NLGenerationResponse]:
    return generation_service.get_nl_generations(
        page, page_size, order, ascend, api_key.organization_id
    )


@router.get("/nl-generations/{id}")
async def get_nl_generation(
    id: ObjectIdString,
    api_key: str = Security(get_api_key),
) -> NLGenerationResponse:
    return generation_service.get_nl_generation(id, api_key.organization_id)


@router.get("/sql-generations/{id}/execute")
async def execute_sql_generation(
    id: ObjectIdString,
    max_rows: int = 100,
    api_key: str = Security(get_api_key),
) -> list[dict]:
    return await generation_service.execute_sql_generation(
        id, max_rows, api_key.organization_id
    )


@router.get("/sql-generations/{id}/csv-file")
async def export_csv_file(
    id: ObjectIdString, api_key: str = Security(get_api_key)
) -> StreamingResponse:
    return await generation_service.export_csv_file(id, api_key.organization_id)

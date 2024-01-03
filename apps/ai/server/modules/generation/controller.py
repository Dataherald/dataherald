from fastapi import APIRouter, Security, status

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
from utils.auth import get_api_key

router = APIRouter(
    prefix="/api",
    responses={404: {"description": "Not found"}},
)

generation_service = GenerationService()


@router.post("/prompts", status_code=status.HTTP_201_CREATED)
async def create_prompt(
    prompt_request: PromptRequest,
    api_key: str = Security(get_api_key),
) -> PromptResponse:
    return await generation_service.create_prompt(
        prompt_request, api_key.organization_id
    )


@router.post("/prompts/sql-generations")
async def create_prompt_sql_generation(
    question_request: PromptSQLGenerationRequest,
    api_key: str = Security(get_api_key),
) -> SQLGenerationResponse:
    return await generation_service.create_prompt_sql_generation(
        question_request, api_key.organization_id
    )


@router.post("/prompts/sql-generations/nl-generations")
async def create_prompt_sql_nl_generation(
    prompt_sql_nl_generation_request: PromptSQLNLGenerationRequest,
    api_key: str = Security(get_api_key),
) -> NLGenerationResponse:
    return await generation_service.create_prompt_sql_nl_generation(
        prompt_sql_nl_generation_request, api_key.organization_id
    )


@router.post("/prompts/{id}/sql-generations")
async def create_sql_generation(
    id: str,
    sql_generation_request: SQLGenerationRequest,
    api_key: str = Security(get_api_key),
) -> SQLGenerationResponse:
    return await generation_service.create_sql_generation(
        id, sql_generation_request, api_key.organization_id
    )


@router.post("/prompts/{id}/sql-generations/nl-generations")
async def create_sql_nl_generation(
    id: str,
    sql_nl_generation_request: SQLNLGenerationRequest,
    api_key: str = Security(get_api_key),
) -> NLGenerationResponse:
    return await generation_service.create_sql_nl_generation(
        id, sql_nl_generation_request, api_key.organization_id
    )


@router.post("/sql-generations/{id}/nl-generations")
async def create_nl_generation(
    id: str,
    nl_generation_request: NLGenerationRequest,
    api_key: str = Security(get_api_key),
) -> NLGenerationResponse:
    return await generation_service.create_nl_generation(
        id, nl_generation_request, api_key.organization_id
    )


@router.get("/prompts")
async def get_prompts(
    page: int = 0,
    page_size: int = 20,
    order: str = "created_at",
    ascend: bool = False,
    api_key: str = Security(get_api_key),
) -> list[PromptResponse]:
    return generation_service.get_prompts(
        page, page_size, order, ascend, api_key.organization_id
    )


@router.get("/prompts/{id}")
async def get_prompt(
    id: str,
    api_key: str = Security(get_api_key),
) -> PromptResponse:
    return generation_service.get_prompt(id, api_key.organization_id)


@router.get("/prompts/{id}/sql-generations")
async def get_sql_generations_by_prompt_id(
    id: str,
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
    id: str,
    api_key: str = Security(get_api_key),
) -> SQLGenerationResponse:
    return generation_service.get_sql_generation(id, api_key.organization_id)


@router.get("/sql-generations/{id}/nl-generations")
async def get_nl_generations_by_sql_generation_id(
    id: str,
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
    id: str,
    api_key: str = Security(get_api_key),
) -> NLGenerationResponse:
    return generation_service.get_nl_generation(id, api_key.organization_id)


@router.get("/sql-generations/{id}/execute")
async def execute_sql_generation(
    id: str,
    max_rows: int = 100,
    api_key: str = Security(get_api_key),
) -> tuple[str, dict]:
    return await generation_service.execute_sql_generation(
        id, max_rows, api_key.organization_id
    )

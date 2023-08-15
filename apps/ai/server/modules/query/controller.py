from fastapi import APIRouter

from modules.query.models.requests import QueryEditRequest, SQLQueryRequest
from modules.query.models.responses import QueryListResponse, QueryResponse
from modules.query.service import QueriesService

router = APIRouter(
    prefix="/query",
    responses={404: {"description": "Not found"}},
)

query_service = QueriesService()


@router.get("/list")
async def get_queries(
    page: int = 0,
    page_size: int = 20,
    order: str = "question_date",
    ascend: bool = True,
) -> list[QueryListResponse]:
    return query_service.get_queries(
        page=page, page_size=page_size, order=order, ascend=ascend
    )


@router.get("/{query_id}")
async def get_query(query_id: str) -> QueryResponse:
    return query_service.get_query(query_id)


@router.patch("/{query_id}")
async def patch_query(query_id: str, query_request: QueryEditRequest) -> QueryResponse:
    return await query_service.patch_query(query_id, query_request)


@router.post("/{query_id}/execution")
async def run_query(query_id: str, query_request: SQLQueryRequest) -> QueryResponse:
    return await query_service.run_query(query_id, query_request)

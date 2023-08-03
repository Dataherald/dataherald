from fastapi import APIRouter

from modules.query.models.requests import QueryEditRequest, SQLQueryRequest
from modules.query.models.responses import QueryListResponse, QueryResponse
from modules.query.service import QueriesService

router = APIRouter(
    prefix="/query",
    responses={404: {"description": "Not found"}},
)


@router.get("/list")
async def get_queries(
    page: int = 0,
    page_size: int = 20,
    order: str = "created_at",
    ascend: bool = True,
) -> list[QueryListResponse]:
    return QueriesService().get_queries(
        page=page, page_size=page_size, order=order, ascend=ascend
    )


@router.get("/{query_id}")
async def get_query(query_id: str) -> QueryResponse:
    return QueriesService().get_query(query_id)


@router.patch("/{query_id}")
async def patch_query(query_id: str, data: QueryEditRequest) -> QueryResponse:
    return QueriesService().patch_query(query_id, data)


@router.post("/{query_id}/execution")
async def run_query(query_id: str, data: SQLQueryRequest) -> QueryResponse:
    return QueriesService().run_query(query_id, data)

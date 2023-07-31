from fastapi import APIRouter

from modules.queries.models.responses import QueryResponse
from modules.queries.service import QueriesService

router = APIRouter(
    prefix="/queries",
)


@router.get("/{query_id}")
async def get_query(query_id: str) -> QueryResponse:
    return QueriesService().get_query(query_id)


@router.get("/")
async def get_queries(
    page: int = 0,
    page_size: int = 20,
    order: str = "created_at",
    ascend: bool = True,
) -> list[QueryResponse]:
    return QueriesService().get_queries(
        page=page, page_size=page_size, order=order, ascend=ascend
    )

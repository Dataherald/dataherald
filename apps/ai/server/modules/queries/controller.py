from fastapi import APIRouter

from modules.queries.model import QueriesReponse, QueryResponse
from modules.queries.service import QueriesService

router = APIRouter(
    prefix="/queries",
)


@router.get("/{query_id}")
async def get_query(query_id: str, db_alias: str) -> QueryResponse:
    return QueriesService.get_query(db_alias, query_id)


@router.get("/")
async def get_queries(
    db_alias: str,
    limit: int,
    skip: int = 0,
    order: str = "created_at",
    ascend: bool = True,
) -> QueriesReponse:
    return QueriesService.get_queries(db_alias, limit, skip, order, ascend)

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from modules.query.models.requests import QueryEditRequest, SQLQueryRequest
from modules.query.models.responses import QueryListResponse, QueryResponse
from modules.query.service import QueryService
from utils.auth import Authorize, VerifyToken

router = APIRouter(
    prefix="/query",
    responses={404: {"description": "Not found"}},
)

token_auth_scheme = HTTPBearer()
authorize = Authorize()
query_service = QueryService()


@router.get("/list")
async def get_queries(
    page: int = 0,
    page_size: int = 20,
    order: str = "question_date",
    ascend: bool = True,
    token: str = Depends(token_auth_scheme),
) -> list[QueryListResponse]:
    org_id = authorize.user_and_get_org_id(VerifyToken(token.credentials).verify())
    return query_service.get_queries(
        page=page, page_size=page_size, order=order, ascend=ascend, org_id=org_id
    )


@router.get("/{query_id}")
async def get_query(
    query_id: str, token: str = Depends(token_auth_scheme)
) -> QueryResponse:
    org_id = authorize.user_and_get_org_id(VerifyToken(token.credentials).verify())
    authorize.query_in_organization(query_id, str(org_id))
    return query_service.get_query(query_id)


@router.patch("/{query_id}")
async def patch_query(
    query_id: str,
    query_request: QueryEditRequest,
    token: str = Depends(token_auth_scheme),
) -> QueryResponse:
    org_id = authorize.user_and_get_org_id(VerifyToken(token.credentials).verify())
    authorize.query_in_organization(query_id, str(org_id))
    return await query_service.patch_query(query_id, query_request)


@router.post("/{query_id}/execution")
async def run_query(
    query_id: str,
    query_request: SQLQueryRequest,
    token: str = Depends(token_auth_scheme),
) -> QueryResponse:
    org_id = authorize.user_and_get_org_id(VerifyToken(token.credentials).verify())
    authorize.query_in_organization(query_id, str(org_id))
    return await query_service.run_query(query_id, query_request)

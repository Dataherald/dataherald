from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from config import auth_settings
from modules.organization.service import OrganizationService
from modules.query.models.requests import (
    QueryExecutionRequest,
    QueryUpdateRequest,
    QuestionRequest,
)
from modules.query.models.responses import (
    QueryListResponse,
    QueryResponse,
    QuerySlackResponse,
)
from modules.query.service import QueryService
from utils.auth import Authorize, VerifyToken, test_organization

router = APIRouter(
    prefix="/query",
    responses={404: {"description": "Not found"}},
)

token_auth_scheme = HTTPBearer()
authorize = Authorize()
query_service = QueryService()
org_service = OrganizationService()


@router.post("/answer")
async def answer_question(
    question_request: QuestionRequest,
    token: str = Depends(token_auth_scheme),
) -> QuerySlackResponse:
    if not auth_settings.auth_enabled:
        organization = test_organization
    else:
        VerifyToken(token.credentials)
        organization = org_service.get_organization_by_slack_workspace_id(
            question_request.slack_workspace_id
        )
    return await query_service.answer_question(question_request, organization)


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


@router.get("/{id}")
async def get_query(id: str, token: str = Depends(token_auth_scheme)) -> QueryResponse:
    org_id = authorize.user_and_get_org_id(VerifyToken(token.credentials).verify())
    authorize.query_in_organization(id, org_id)
    return query_service.get_query(id)


@router.patch("/{id}")
async def patch_query(
    id: str,
    query_request: QueryUpdateRequest,
    token: str = Depends(token_auth_scheme),
) -> QueryResponse:
    user = authorize.user(VerifyToken(token.credentials).verify())
    organization = authorize.get_organization_by_user(user)
    authorize.query_in_organization(id, str(organization.id))
    return await query_service.patch_query(id, query_request, organization, user)


@router.post("/{id}/execution")
async def run_query(
    id: str,
    sql_query: QueryExecutionRequest,
    token: str = Depends(token_auth_scheme),
) -> QueryResponse:
    org_id = authorize.user_and_get_org_id(VerifyToken(token.credentials).verify())
    authorize.query_in_organization(id, org_id)
    return await query_service.run_query(id, sql_query)

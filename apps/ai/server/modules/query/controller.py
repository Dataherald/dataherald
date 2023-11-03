from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from modules.organization.service import OrganizationService
from modules.query.models.requests import (
    QueryUpdateRequest,
    QuestionRequest,
    SQLAnswerRequest,
)
from modules.query.models.responses import (
    MessageResponse,
    QueryListResponse,
    QueryResponse,
    QuerySlackResponse,
)
from modules.query.service import QueryService
from utils.auth import Authorize, VerifyToken

router = APIRouter(
    prefix="/query",
    responses={404: {"description": "Not found"}},
)

token_auth_scheme = HTTPBearer()
authorize = Authorize()
query_service = QueryService()
org_service = OrganizationService()


@router.post("/answer", status_code=status.HTTP_201_CREATED)
async def answer_question(
    question_request: QuestionRequest,
    token: str = Depends(token_auth_scheme),
) -> QuerySlackResponse:
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
    question_id: str = None,
    token: str = Depends(token_auth_scheme),
) -> list[QueryListResponse]:
    org_id = authorize.user(VerifyToken(token.credentials).verify()).organization_id
    return query_service.get_queries(
        page=page,
        page_size=page_size,
        order=order,
        ascend=ascend,
        question_id=question_id,
        org_id=org_id,
    )


@router.get("/{id}")
async def get_query(id: str, token: str = Depends(token_auth_scheme)) -> QueryResponse:
    org_id = authorize.user(VerifyToken(token.credentials).verify()).organization_id
    authorize.query_in_organization(id, org_id)
    return query_service.get_query(id)


@router.patch("/{id}")
async def update_query(
    id: str,
    query_request: QueryUpdateRequest,
    token: str = Depends(token_auth_scheme),
) -> QueryResponse:
    user = authorize.user(VerifyToken(token.credentials).verify())
    organization = authorize.get_organization_by_user_response(user)
    authorize.query_in_organization(id, str(organization.id))
    return await query_service.update_query(id, query_request, user, organization)


@router.post("/{id}/sql-answer", status_code=status.HTTP_201_CREATED)
async def generate_sql_answer(
    id: str,
    sql_answer_request: SQLAnswerRequest,
    token: str = Depends(token_auth_scheme),
) -> QueryResponse:
    user = authorize.user(VerifyToken(token.credentials).verify())
    authorize.query_in_organization(id, user.organization_id)
    return await query_service.generate_sql_answer(id, sql_answer_request, user)


@router.patch("/{id}/message", status_code=status.HTTP_200_OK)
async def generate_message(
    id: str,
    token: str = Depends(token_auth_scheme),
) -> MessageResponse:
    user = authorize.user(VerifyToken(token.credentials).verify())
    authorize.query_in_organization(id, user.organization_id)
    return await query_service.generate_message(id)


@router.post("/{id}/message", status_code=status.HTTP_200_OK)
async def send_message(
    id: str,
    token: str = Depends(token_auth_scheme),
):
    user = authorize.user(VerifyToken(token.credentials).verify())
    authorize.query_in_organization(id, user.organization_id)
    organization = authorize.get_organization_by_user_response(user)
    return await query_service.send_message(id, organization)

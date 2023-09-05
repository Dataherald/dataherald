from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from config import auth_settings
from modules.k2_core.models.requests import QuestionRequest
from modules.k2_core.models.responses import NLQuerySlackResponse
from modules.k2_core.service import K2Service
from modules.organization.service import OrganizationService
from utils.auth import VerifyToken, test_organization

router = APIRouter(
    prefix="/k2",
    responses={404: {"description": "Not found"}},
)

token_auth_scheme = HTTPBearer()

k2_service = K2Service()
org_service = OrganizationService()


@router.post("/question")
async def answer_question(
    question_request: QuestionRequest,
    token: str = Depends(token_auth_scheme),
) -> NLQuerySlackResponse:
    if not auth_settings.auth_enabled:
        organization = test_organization
    else:
        VerifyToken(token.credentials)
        organization = org_service.get_organization_by_slack_workspace_id(
            question_request.slack_workspace_id
        )
    return await k2_service.answer_question(question_request, organization)


@router.get("/heartbeat")
async def heartbeat():
    return await k2_service.heartbeat()

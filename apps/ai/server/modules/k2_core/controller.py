from fastapi import APIRouter

from modules.k2_core.models.requests import QuestionRequest
from modules.k2_core.models.responses import NLQueryResponse
from modules.k2_core.service import K2Service
from modules.organization.service import OrganizationService
from utils.auth import test_organization

router = APIRouter(
    prefix="/k2",
    responses={404: {"description": "Not found"}},
)

k2_service = K2Service()
org_service = OrganizationService()


@router.post("/question")
async def answer_question(question_request: QuestionRequest) -> NLQueryResponse:
    if question_request.user.slack_workspace_id == test_organization.slack_workspace_id:
        organization = test_organization
    else:
        organization = org_service.get_organization_with_slack_workspace_id(
            question_request.user.slack_workspace_id
        )
    return await k2_service.answer_question(question_request, organization)


@router.get("/heartbeat")
async def heartbeat():
    return await k2_service.heartbeat()

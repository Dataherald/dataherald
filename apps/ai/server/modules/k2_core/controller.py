from fastapi import APIRouter

from modules.k2_core.models.requests import QuestionRequest
from modules.k2_core.models.responses import NLQueryResponse
from modules.k2_core.service import K2Service

router = APIRouter(
    prefix="/k2",
    responses={404: {"description": "Not found"}},
)

k2_service = K2Service()


@router.post("/question")
async def answer_question(question_request: QuestionRequest) -> NLQueryResponse:
    return await k2_service.answer_question(question_request)


@router.get("/heartbeat")
async def heartbeat():
    return await k2_service.heartbeat()

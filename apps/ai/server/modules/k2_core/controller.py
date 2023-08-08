from fastapi import APIRouter

from modules.k2_core.models.requests import QuestionRequest
from modules.k2_core.models.responses import NLQueryResponse
from modules.k2_core.service import K2Service

router = APIRouter(
    prefix="/k2",
    responses={404: {"description": "Not found"}},
)

# will probably divide k2 into evaluation, sql_generation, and db_connection


@router.post("/question")
async def answer_question(question: QuestionRequest) -> NLQueryResponse:
    return await K2Service().answer_question(question)


@router.get("/heartbeat")
async def heartbeat():
    return await K2Service().heartbeat()

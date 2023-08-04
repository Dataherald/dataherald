from typing import List

from fastapi import APIRouter

from modules.k2_core.models.entities import DataDefinitionType, SSHSettings
from modules.k2_core.models.requests import EvaluationRequest
from modules.k2_core.models.responses import Evaluation, NLQueryResponse
from modules.k2_core.service import K2Service

router = APIRouter(
    prefix="/k2",
    responses={404: {"description": "Not found"}},
)

# will probably divide k2 into evaluation, sql_generation, and db_connection


@router.post("/question")
async def answer_question(question: str) -> NLQueryResponse:
    return await K2Service().answer_question(question)


@router.post("/question/evaluate")
async def evaluate_question(evaluation: EvaluationRequest) -> Evaluation:
    return await K2Service().evaluate(evaluation)


@router.post("/database")
async def connect_database(
    alias: str,
    use_ssh: bool,
    connection_uri: str | None = None,
    ssh_settings: SSHSettings | None = None,
) -> bool:
    return await K2Service().connect_database(
        alias, use_ssh, connection_uri, ssh_settings
    )


@router.post("/golden-record")
async def add_golden_records(golden_records: List) -> bool:
    return await K2Service().add_golden_records(golden_records)


@router.post("/data-definition")
async def add_data_definition(uri: str, data: DataDefinitionType) -> bool:
    return await K2Service().add_data_definition(uri, data)


@router.get("/heartbeat")
async def heartbeat():
    return await K2Service().heartbeat()

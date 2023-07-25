from typing import List

from fastapi import APIRouter

from modules.k2_core.model import DataDefinitionType, SSHSettings
from modules.k2_core.service import K2Service

router = APIRouter(
    prefix="/k2",
    responses={404: {"description": "Not found"}},
)

# will probably divide k2 into evaluation, sql_generation, and db_connection


@router.post("/question")
async def answer_question(question: str, db_alias: str):
    return K2Service().answer_question(question, db_alias)


@router.post("/question/evaluate")
async def evaluate_question(question: str, golden_sql: str):
    return K2Service().evaluate(question, golden_sql)


@router.post("/database")
async def connect_database(
    alias: str,
    use_ssh: bool,
    connection_uri: str | None = None,
    ssh_settings: SSHSettings | None = None,
) -> bool:
    return K2Service().connect_database(alias, use_ssh, connection_uri, ssh_settings)


@router.post("/golden-record")
async def add_golden_records(golden_records: List):
    return K2Service().add_golden_records(golden_records)


@router.post("/data-definition")
async def add_data_definition(uri: str, type: DataDefinitionType):
    return K2Service().add_data_definition(uri, type)


@router.get("/heartbeat")
async def heartbeat():
    return K2Service().heartbeat()

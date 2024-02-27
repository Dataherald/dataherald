import httpx

from config import settings
from exceptions.exception_handlers import raise_engine_exception
from modules.db_connection.service import DBConnectionService
from modules.finetuning.models.entities import (
    DHFinetuningMetadata,
    Finetuning,
    FinetuningMetadata,
)
from modules.finetuning.models.exceptions import (
    FinetuningAliasExistsError,
    FinetuningNotFoundError,
)
from modules.finetuning.models.requests import FinetuningRequest
from modules.finetuning.models.responses import AggrFinetuning
from modules.finetuning.repository import FinetuningRepository
from modules.golden_sql.service import GoldenSQLService
from utils.analytics import Analytics, EventName, EventType
from utils.misc import reserved_key_in_metadata


class FinetuningService:
    def __init__(self):
        self.repo = FinetuningRepository()
        self.db_connection_service = DBConnectionService()
        self.golden_sql_service = GoldenSQLService()
        self.analytics = Analytics()

    async def get_finetuning_jobs(
        self, org_id: str, db_connection_id: str = None
    ) -> list[AggrFinetuning]:
        finetuning_jobs = []
        if db_connection_id:
            db_connections = [
                self.db_connection_service.get_db_connection_in_org(
                    db_connection_id, org_id
                )
            ]
        else:
            db_connections = self.db_connection_service.get_db_connections(org_id)
        for db_connection in db_connections:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    settings.engine_url + "/finetunings",
                    params={"db_connection_id": db_connection.id},
                    timeout=settings.default_engine_timeout,
                )
                raise_engine_exception(response, org_id=org_id)
                finetuning_jobs += [
                    AggrFinetuning(
                        **finetuning_job,
                        db_connection_alias=db_connection.alias,
                    )
                    for finetuning_job in response.json()
                ]
        return finetuning_jobs

    async def get_finetuning_job(
        self, finetuning_id: str, org_id: str
    ) -> AggrFinetuning:
        self.get_finetuning_job_in_org(finetuning_id, org_id)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                settings.engine_url + f"/finetunings/{finetuning_id}",
                timeout=settings.default_engine_timeout,
            )
            raise_engine_exception(response, org_id=org_id)
            finetuning_job = Finetuning(**response.json())
            db_connection = self.db_connection_service.get_db_connection_in_org(
                finetuning_job.db_connection_id, org_id
            )
            return AggrFinetuning(
                **finetuning_job.dict(), db_connection_alias=db_connection.alias
            )

    async def create_finetuning_job(
        self, finetuning_request: FinetuningRequest, org_id: str
    ) -> AggrFinetuning:
        reserved_key_in_metadata(finetuning_request.metadata)
        db_connection = self.db_connection_service.get_db_connection_in_org(
            finetuning_request.db_connection_id, org_id
        )

        finetuning = self.repo.get_finetuning_job_by_alias(
            finetuning_request.alias, org_id
        )
        if finetuning:
            raise FinetuningAliasExistsError(finetuning.id, org_id)

        finetuning_request.metadata = FinetuningMetadata(
            **finetuning_request.metadata,
            dh_internal=DHFinetuningMetadata(organization_id=org_id),
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url + "/finetunings",
                json=finetuning_request.dict(exclude_unset=True),
            )
            raise_engine_exception(response, org_id=org_id)

            aggr_finetuning = AggrFinetuning(
                **response.json(), db_connection_alias=db_connection.alias
            )

            self.analytics.track(
                org_id,
                EventName.finetuning_created,
                EventType.finetuning_event(
                    id=aggr_finetuning.id,
                    organization_id=org_id,
                    db_connection_id=aggr_finetuning.db_connection_id,
                    db_connection_alias=aggr_finetuning.db_connection_alias,
                    model_provider=aggr_finetuning.base_llm.model_provider,
                    model_name=aggr_finetuning.base_llm.model_name,
                    golden_sql_quantity=self.get_finetuning_golden_sql_count(
                        finetuning_request, org_id
                    ),
                ),
            )

            return aggr_finetuning

    async def cancel_finetuning_job(
        self, finetuning_id: str, org_id: str
    ) -> AggrFinetuning:
        finetuning = self.get_finetuning_job_in_org(finetuning_id, org_id)
        db_connection = self.db_connection_service.get_db_connection_in_org(
            finetuning.db_connection_id, org_id
        )
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url + f"/finetunings/{finetuning_id}/cancel",
            )
            raise_engine_exception(response, org_id=org_id)
            return AggrFinetuning(
                **response.json(), db_connection_alias=db_connection.alias
            )

    def get_finetuning_job_in_org(self, finetuning_id: str, org_id: str) -> Finetuning:
        finetuning_job = self.repo.get_finetuning_job(finetuning_id, org_id)
        if not finetuning_job:
            raise FinetuningNotFoundError(finetuning_id, org_id)
        return finetuning_job

    def is_gpt_4_model(self, model_name: str) -> bool:
        return "gpt-4" in model_name

    def get_finetuning_golden_sql_count(
        self, finetuning_request: FinetuningRequest, org_id: str
    ) -> int:
        # if golden_sqls are provided, use the length of the list
        if finetuning_request.golden_sqls:
            return len(finetuning_request.golden_sqls)
        # if not, get all golden_sqls from the db_connection
        return len(
            self.golden_sql_service.get_golden_sqls(
                0, 0, "created_at", False, org_id, finetuning_request.db_connection_id
            )
        )

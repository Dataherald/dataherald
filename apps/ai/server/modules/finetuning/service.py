import httpx
from fastapi import HTTPException, status

from config import settings
from modules.db_connection.service import DBConnectionService
from modules.finetuning.models.entities import (
    DHFinetuningMetadata,
    Finetuning,
    FinetuningMetadata,
)
from modules.finetuning.models.requests import FinetuningRequest
from modules.finetuning.models.responses import AggrFinetuning
from modules.finetuning.repository import FinetuningRepository
from utils.exception import raise_for_status
from utils.misc import reserved_key_in_metadata


class FinetuningService:
    def __init__(self):
        self.repo = FinetuningRepository()
        self.db_connection_service = DBConnectionService()

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
                raise_for_status(response.status_code, response.text)
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
            raise_for_status(response.status_code, response.text)
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

        finetuning_request.metadata = FinetuningMetadata(
            **finetuning_request.metadata,
            dh_internal=DHFinetuningMetadata(organization_id=org_id),
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url + "/finetunings",
                json=finetuning_request.dict(exclude_unset=True),
            )
            raise_for_status(response.status_code, response.text)
            return AggrFinetuning(
                **response.json(), db_connection_alias=db_connection.alias
            )

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
            raise_for_status(response.status_code, response.text)
            return AggrFinetuning(
                **response.json(), db_connection_alias=db_connection.alias
            )

    def get_finetuning_job_in_org(self, finetuning_id: str, org_id: str) -> Finetuning:
        finetuning_job = self.repo.get_finetuning_job(finetuning_id, org_id)
        if not finetuning_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Finetuning not found",
            )
        return finetuning_job

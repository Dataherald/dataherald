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
from modules.finetuning.models.responses import FinetuningResponse
from modules.finetuning.repository import FinetuningRepository
from utils.exception import raise_for_status
from utils.misc import reserved_key_in_metadata


class FinetuningService:
    def __init__(self):
        self.repo = FinetuningRepository()
        self.db_connection_service = DBConnectionService()

    def get_finetuning_jobs(
        self, db_connection_id: str, org_id: str
    ) -> list[FinetuningResponse]:
        return self.repo.get_finetuning_jobs(db_connection_id, org_id)

    def get_finetuning_job(self, finetuning_id: str, org_id: str) -> FinetuningResponse:
        return self.get_finetuning_job_in_org(finetuning_id, org_id)

    async def create_finetuning_job(
        self, finetuning_request: FinetuningRequest, org_id: str
    ):
        reserved_key_in_metadata(finetuning_request.metadata)
        self.db_connection_service.get_db_connection_in_org(
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
            return FinetuningResponse(**response.json())

    async def cancel_finetuning_job(
        self, finetuning_id: str, org_id: str
    ) -> FinetuningResponse:
        self.get_finetuning_job_in_org(finetuning_id, org_id)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url + f"/finetunings/{finetuning_id}/cancel",
            )
            raise_for_status(response.status_code, response.text)
            return FinetuningResponse(**response.json())

    def get_finetuning_job_in_org(self, finetuning_id: str, org_id: str) -> Finetuning:
        finetuning_job = self.repo.get_finetuning_job(finetuning_id, org_id)
        if not finetuning_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Finetuning not found",
            )
        return finetuning_job

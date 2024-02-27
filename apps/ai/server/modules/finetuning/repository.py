from bson import ObjectId

from config import FINETUNING_COL
from database.mongo import MongoDB
from modules.finetuning.models.entities import Finetuning


class FinetuningRepository:
    def get_finetuning_jobs(self, db_connection_id, org_id) -> list[Finetuning]:
        finetuning_jobs = MongoDB.find(
            FINETUNING_COL,
            {
                "db_connection_id": db_connection_id,
                "metadata.dh_internal.organization_id": org_id,
            },
        )
        return (
            [
                Finetuning(id=str(finetuning_job["_id"]), **finetuning_job)
                for finetuning_job in finetuning_jobs
            ]
            if finetuning_jobs
            else []
        )

    def get_finetuning_job(self, finetuning_id: str, org_id: str) -> Finetuning:
        finetuning_job = MongoDB.find_one(
            FINETUNING_COL,
            {
                "_id": ObjectId(finetuning_id),
                "metadata.dh_internal.organization_id": org_id,
            },
        )
        return (
            Finetuning(id=str(finetuning_job["_id"]), **finetuning_job)
            if finetuning_job
            else None
        )

    def get_finetuning_job_by_alias(self, alias: str, org_id: str) -> Finetuning:
        finetuning_job = MongoDB.find_one(
            FINETUNING_COL,
            {
                "alias": alias,
                "metadata.dh_internal.organization_id": org_id,
            },
        )
        return (
            Finetuning(id=str(finetuning_job["_id"]), **finetuning_job)
            if finetuning_job
            else None
        )

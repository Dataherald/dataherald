from bson import ObjectId

from config import FINETUNING_COL
from database.mongo import MongoDB
from modules.finetuning.models.entities import Finetuning


class FinetuningRepository:
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

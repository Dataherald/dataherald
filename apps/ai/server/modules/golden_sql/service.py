from typing import Dict

import httpx
from bson import ObjectId
from fastapi import HTTPException, status

from config import settings
from modules.golden_sql.models.entities import GoldenSQL, GoldenSQLRef, GoldenSQLSource
from modules.golden_sql.models.requests import GoldenSQLRequest
from modules.golden_sql.models.responses import GoldenSQLResponse
from modules.golden_sql.repository import GoldenSQLRepository


class GoldenSQLService:
    def __init__(self):
        self.repo = GoldenSQLRepository()

    def get_golden_sql(self, id: str) -> GoldenSQL:
        object_id = ObjectId(id)
        golden_sql_ref = self.repo.get_golden_sql_ref(object_id)
        golden_sql = self.repo.get_golden_sql(golden_sql_ref.golden_sql_id)
        if golden_sql:
            return self._get_mapped_golden_sql_response(golden_sql, golden_sql_ref)

        return None

    def get_golden_sqls(
        self,
        page: int,
        page_size: int,
        order: str,
        ascend: bool,  # noqa: ARG002
        org_id: str,
    ) -> list[GoldenSQL]:
        golden_sql_refs = self.repo.get_golden_sql_refs(
            skip=page * page_size, limit=page_size, order=order, org_id=ObjectId(org_id)
        )

        object_ids = [gsr.golden_sql_id for gsr in golden_sql_refs]

        golden_sqls = self.repo.get_golden_sqls(object_ids)
        golden_sqls_dict: Dict[ObjectId, GoldenSQL] = {}
        for gs in golden_sqls:
            golden_sqls_dict[gs.id] = gs
        return [
            self._get_mapped_golden_sql_response(
                golden_sqls_dict[gsr.golden_sql_id], gsr
            )
            for gsr in golden_sql_refs
        ]

    def get_verified_golden_sql_ref(self, query_response_id: str) -> GoldenSQLRef:
        return self.repo.get_verified_golden_sql_ref(ObjectId(query_response_id))

    async def add_golden_sql(
        self,
        golden_sql_request: GoldenSQLRequest,
        org_id: str,
        source: GoldenSQLSource,
        query_response_id: str = None,
    ) -> GoldenSQLResponse:
        async with httpx.AsyncClient() as client:
            # if already exist, delete golden_sql_ref and call delete /golden-records
            if query_response_id:
                golden_sql_ref = self.repo.get_verified_golden_sql_ref(
                    ObjectId(query_response_id)
                )
                if golden_sql_ref:
                    await self.delete_golden_sql("", query_response_id)

            # add golden_sql using core
            response = await client.post(
                settings.k2_core_url + "/golden-records",
                # core should have consistent request body
                json=[golden_sql_request.dict()],
                timeout=settings.default_k2_core_timeout,
            )
            response.raise_for_status()
            response_json = response.json()[0]
            golden_sql = GoldenSQL(**response_json)
            golden_sql.id = response_json["id"]
            # add golden_sql_ref
            self.repo.add_golden_sql_ref(
                ObjectId(golden_sql.id),
                ObjectId(org_id),
                source,
                query_response_id=ObjectId(query_response_id),
            )
            golden_sql_ref = self.repo.get_golden_sql_ref(ObjectId(golden_sql.id))
            return self._get_mapped_golden_sql_response(golden_sql, golden_sql_ref)

    async def delete_golden_sql(self, id: str, query_response_id: str = None):
        if query_response_id:
            golden_sql_ref = self.repo.get_verified_golden_sql_ref(
                ObjectId(query_response_id)
            )
            id = golden_sql_ref.golden_sql_id
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                settings.k2_core_url + f"/golden-records/{id}",
                timeout=settings.default_k2_core_timeout,
            )
            response.raise_for_status()
            if response.json()["status"]:
                if query_response_id:
                    matched_count = self.repo.delete_verified_golden_sql_ref(
                        ObjectId(query_response_id)
                    )
                else:
                    matched_count = self.repo.delete_golden_sql_ref(ObjectId(id))
                if matched_count == 1:
                    return {"id": id}

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    def _get_mapped_golden_sql_response(
        self,
        golden_sql: GoldenSQL,
        golden_sql_ref: GoldenSQLRef,
    ) -> GoldenSQLResponse:
        return GoldenSQLResponse(
            id=str(golden_sql.id),
            question=golden_sql.question,
            sql_query=golden_sql.sql_query,
            db_alias=golden_sql.db_alias,
            created_time=golden_sql_ref.created_time,
            organization_id=str(golden_sql_ref.organization_id),
            source=golden_sql_ref.source,
            verified_query_id=str(golden_sql_ref.query_response_id),
        )

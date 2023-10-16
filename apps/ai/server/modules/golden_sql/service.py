from datetime import datetime, timezone
from typing import Dict, List

import httpx
from bson import ObjectId
from fastapi import HTTPException, status

from config import settings
from modules.golden_sql.models.entities import GoldenSQL, GoldenSQLRef, GoldenSQLSource
from modules.golden_sql.models.requests import GoldenSQLRequest
from modules.golden_sql.models.responses import GoldenSQLResponse
from modules.golden_sql.repository import GoldenSQLRepository
from utils.exception import raise_for_status


class GoldenSQLService:
    def __init__(self):
        self.repo = GoldenSQLRepository()

    def get_golden_sql(self, golden_id: str) -> GoldenSQLResponse:
        golden_sql_ref = self.repo.get_golden_sql_ref(golden_id)
        golden_sql = self.repo.get_golden_sql(str(golden_sql_ref.golden_sql_id))
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
    ) -> list[GoldenSQLResponse]:
        golden_sql_refs = self.repo.get_golden_sql_refs(
            skip=page * page_size, limit=page_size, order=order, org_id=org_id
        )

        golden_ids = [str(gsr.golden_sql_id) for gsr in golden_sql_refs]

        golden_sqls = self.repo.get_golden_sqls(golden_ids)
        golden_sqls_dict: Dict[ObjectId, GoldenSQL] = {}
        for gs in golden_sqls:
            golden_sqls_dict[gs.id] = gs
        return [
            self._get_mapped_golden_sql_response(
                golden_sqls_dict[gsr.golden_sql_id], gsr
            )
            for gsr in golden_sql_refs
        ]

    def get_verified_golden_sql_ref(self, query_id: str) -> GoldenSQLRef:
        return self.repo.get_verified_golden_sql_ref(query_id)

    async def add_verified_query_golden_sql(
        self,
        golden_sql_request: GoldenSQLRequest,
        org_id: str,
        query_id: str,
    ) -> GoldenSQLResponse:
        golden_sql_ref = self.repo.get_verified_golden_sql_ref(query_id)
        # if already exist, delete golden_sql_ref and call delete /golden-records
        if golden_sql_ref:
            await self.delete_golden_sql("", query_id)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.k2_core_url + "/golden-records",
                json=[golden_sql_request.dict()],
                timeout=settings.default_k2_core_timeout,
            )
            raise_for_status(response.status_code, response.text)
            response_json = response.json()[0]
            golden_sql = GoldenSQL(_id=ObjectId(response_json["id"]), **response_json)

            display_id = self.repo.get_next_display_id(org_id)

            golden_sql_ref_data = GoldenSQLRef(
                golden_sql_id=golden_sql.id,
                organization_id=ObjectId(org_id),
                source=GoldenSQLSource.VERIFIED_QUERY.value,
                query_id=ObjectId(query_id),
                created_time=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                display_id=display_id,
            )

            # add golden_sql_ref
            self.repo.add_golden_sql_ref(golden_sql_ref_data.dict(exclude={"id"}))
            golden_sql_ref = self.repo.get_golden_sql_ref(str(golden_sql.id))
            return self._get_mapped_golden_sql_response(golden_sql, golden_sql_ref)

    async def add_user_upload_golden_sql(
        self, golden_sql_requests: List[GoldenSQLRequest], org_id: str
    ) -> List[GoldenSQLResponse]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.k2_core_url + "/golden-records",
                json=[
                    golden_sql_request.dict()
                    for golden_sql_request in golden_sql_requests
                ],
                timeout=settings.default_k2_core_timeout,
            )
            raise_for_status(response.status_code, response.text)

            response_jsons = response.json()
            golden_sqls = [
                GoldenSQL(_id=ObjectId(response_json["id"]), **response_json)
                for response_json in response_jsons
            ]

            golden_sql_responses = []

            for golden_sql in golden_sqls:
                display_id = self.repo.get_next_display_id(org_id)

                golden_sql_ref_data = GoldenSQLRef(
                    golden_sql_id=golden_sql.id,
                    organization_id=ObjectId(org_id),
                    source=GoldenSQLSource.USER_UPLOAD.value,
                    created_time=datetime.now(timezone.utc).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    display_id=display_id,
                )

                # add golden_sql_ref
                self.repo.add_golden_sql_ref(golden_sql_ref_data.dict(exclude={"id"}))
                golden_sql_ref = self.repo.get_golden_sql_ref(str(golden_sql.id))
                golden_sql_responses.append(
                    self._get_mapped_golden_sql_response(golden_sql, golden_sql_ref)
                )

            return golden_sql_responses

    async def delete_golden_sql(self, golden_id: str) -> dict:
        golden_sql_ref = self.repo.get_golden_sql_ref(golden_id)

        if golden_sql_ref:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    settings.k2_core_url + f"/golden-records/{golden_id}",
                    timeout=settings.default_k2_core_timeout,
                )
                raise_for_status(response.status_code, response.text)
                if response.json()["status"]:
                    if golden_sql_ref.query_id:
                        matched_count = self.repo.delete_verified_golden_sql_ref(
                            golden_sql_ref.query_id
                        )
                    else:
                        matched_count = self.repo.delete_golden_sql_ref(golden_id)
                    if matched_count == 1:
                        return {"id": golden_id}

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
            db_connection_id=str(golden_sql.db_connection_id),
            created_time=golden_sql_ref.created_time,
            organization_id=str(golden_sql_ref.organization_id),
            source=golden_sql_ref.source,
            verified_query_id=str(golden_sql_ref.query_id),
            display_id=golden_sql_ref.display_id,
            verified_query_display_id=self.repo.get_verified_query_display_id(
                str(golden_sql_ref.query_id)
            )
            if golden_sql_ref.query_id
            else None,
        )

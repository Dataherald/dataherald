from typing import List

import httpx

from config import settings
from exceptions.exception_handlers import raise_engine_exception
from modules.generation.models.entities import GenerationStatus
from modules.generation.service import DBConnectionService
from modules.golden_sql.models.entities import (
    DHGoldenSQLMetadata,
    GoldenSQL,
    GoldenSQLMetadata,
    GoldenSQLSource,
)
from modules.golden_sql.models.exceptions import (
    CannotDeleteGoldenSqlError,
    GoldenSqlNotFoundError,
)
from modules.golden_sql.models.requests import GoldenSQLRequest
from modules.golden_sql.models.responses import AggrGoldenSQL
from modules.golden_sql.repository import GoldenSQLRepository
from utils.analytics import Analytics, EventName, EventType
from utils.misc import reserved_key_in_metadata


class GoldenSQLService:
    def __init__(self):
        self.repo = GoldenSQLRepository()
        self.db_connection_service = DBConnectionService()
        self.analytics = Analytics()

    def get_golden_sql(self, golden_sql_id: str, org_id: str) -> AggrGoldenSQL:
        golden_sql = self.get_golden_sql_in_org(golden_sql_id, org_id)
        return AggrGoldenSQL(
            **golden_sql.dict(),
            db_connection_alias=self.db_connection_service.get_db_connection_in_org(
                golden_sql.db_connection_id, org_id
            ).alias,
        )

    def get_golden_sqls(
        self,
        page: int,
        page_size: int,
        order: str,
        ascend: bool,  # noqa: ARG002
        org_id: str,
        search_term: str = "",
        db_connection_id: str = None,
    ) -> list[AggrGoldenSQL]:
        db_connection_dict = {
            db_connection.id: db_connection
            for db_connection in self.db_connection_service.get_db_connections(org_id)
        }

        golden_sqls = self.repo.get_golden_sqls(
            skip=page * page_size,
            limit=page_size,
            order=order,
            ascend=ascend,
            org_id=org_id,
            search_term=search_term,
            db_connection_id=db_connection_id,
        )
        return [
            AggrGoldenSQL(
                **golden_sql.dict(),
                db_connection_alias=(
                    db_connection_dict[golden_sql.db_connection_id].alias
                    if golden_sql.db_connection_id in db_connection_dict
                    else None
                ),
            )
            for golden_sql in golden_sqls
        ]

    async def add_user_upload_golden_sql(
        self, golden_sql_requests: List[GoldenSQLRequest], org_id: str
    ) -> List[AggrGoldenSQL]:
        display_id = self.repo.get_next_display_id(org_id)
        db_connection_dict = {
            db_connection.id: db_connection
            for db_connection in self.db_connection_service.get_db_connections(org_id)
        }
        for golden_sql_request in golden_sql_requests:
            reserved_key_in_metadata(golden_sql_request.metadata)
            self.db_connection_service.get_db_connection_in_org(
                golden_sql_request.db_connection_id, org_id
            )
            golden_sql_request.metadata = GoldenSQLMetadata(
                **golden_sql_request.metadata,
                dh_internal=DHGoldenSQLMetadata(
                    display_id=display_id,
                    organization_id=org_id,
                    source=GoldenSQLSource.USER_UPLOAD,
                ),
            )

            display_id = f"{display_id[:-5]}{(int(display_id[-5:])+1):05d}"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url + "/golden-sqls",
                json=[
                    golden_sql_request.dict(exclude_unset=True)
                    for golden_sql_request in golden_sql_requests
                ],
                timeout=settings.default_engine_timeout,
            )
            raise_engine_exception(response, org_id=org_id)

            response_jsons = response.json()
            golden_sqls = [
                GoldenSQL(**response_json) for response_json in response_jsons
            ]

            self.analytics.track(
                org_id,
                EventName.golden_sql_created,
                EventType.golden_sql_event(
                    quantity=len(golden_sqls), organization_id=org_id
                ),
            )

            return [
                AggrGoldenSQL(
                    **golden_sql.dict(),
                    db_connection_alias=(
                        db_connection_dict[golden_sql.db_connection_id].alias
                        if golden_sql.db_connection_id in db_connection_dict
                        else None
                    ),
                )
                for golden_sql in golden_sqls
            ]

    # we can avoid cyclic import if we avoid deleting verified golden sql
    async def delete_golden_sql(
        self, golden_sql_id: str, org_id: str, query_status: GenerationStatus = None
    ) -> dict:
        golden_sql = self.get_golden_sql_in_org(golden_sql_id, org_id)

        async with httpx.AsyncClient() as client:
            response = await client.delete(
                settings.engine_url + f"/golden-sqls/{golden_sql_id}",
                timeout=settings.default_engine_timeout,
            )
            raise_engine_exception(response, org_id=org_id)
            if response.json()["status"]:
                if query_status:
                    self.repo.update_generation_status(
                        golden_sql.metadata.dh_internal.prompt_id, query_status
                    )
                return {"id": golden_sql_id}

        raise CannotDeleteGoldenSqlError(golden_sql_id, org_id)

    def get_verified_golden_sql(self, prompt_id: str) -> GoldenSQL:
        return self.repo.get_verified_golden_sql(prompt_id)

    async def add_verified_golden_sql(
        self,
        golden_sql_request: GoldenSQLRequest,
        org_id: str,
        prompt_id: str,
    ) -> GoldenSQL:
        golden_sql = self.repo.get_verified_golden_sql(prompt_id)
        # if already exist, call delete /golden-sqls
        if golden_sql:
            await self.delete_golden_sql(golden_sql.id, org_id)

        display_id = self.repo.get_next_display_id(org_id)

        golden_sql_request.metadata = GoldenSQLMetadata(
            **golden_sql_request.metadata,
            dh_internal=DHGoldenSQLMetadata(
                prompt_id=prompt_id,
                display_id=display_id,
                organization_id=org_id,
                source=GoldenSQLSource.VERIFIED_QUERY,
            ),
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url + "/golden-sqls",
                json=[golden_sql_request.dict(exclude_unset=True)],
                timeout=settings.default_engine_timeout,
            )
            raise_engine_exception(response, org_id=org_id)
            response_json = response.json()[0]

            self.analytics.track(
                org_id,
                EventName.golden_sql_created,
                EventType.golden_sql_event(quantity=1, organization_id=org_id),
            )

            return GoldenSQL(**response_json)

    def get_golden_sql_in_org(self, golden_sql_id: str, org_id: str) -> GoldenSQL:
        golden_sql = self.repo.get_golden_sql(golden_sql_id, org_id)
        if not golden_sql:
            raise GoldenSqlNotFoundError(golden_sql_id, org_id)
        return golden_sql

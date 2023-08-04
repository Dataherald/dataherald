import logging
from typing import List

import httpx

from config import dbsettings, settings
from modules.k2_core.models.entities import DataDefinitionType, SSHSettings
from modules.k2_core.models.responses import Evaluation, NLQueryResponse
from modules.k2_core.repository import K2CoreRepository

logger = logging.getLogger(__name__)


# use request
class K2Service:
    def __init__(self):
        self.repo = K2CoreRepository()

    async def answer_question(self, question: str) -> NLQueryResponse:
        path = "/question"
        params = {"question": question, "db_alias": dbsettings.db_alias}

        response: NLQueryResponse = await self._k2_post_request(path, params=params)
        self.repo.record_response_pointer(response["id"])
        return response

    async def evaluate(self, data) -> Evaluation:
        path = "/question/evaluate"

        return await self._k2_post_request(path, data)

    async def connect_database(
        self,
        alias: str,
        use_ssh: bool,
        connection_uri: str | None = None,
        ssh_settings: SSHSettings | None = None,
    ) -> bool:
        path = "/database"
        data = {
            "alias": alias,
            "use_ssh": use_ssh,
            "connection_uri": connection_uri,
            "ssh_settings": ssh_settings,
        }

        return self._k2_post_request(path, data)

    async def add_golden_records(self, golden_records: List) -> bool:
        path = "/golden-record"
        data = {"golden_records": golden_records}

        return await self._k2_post_request(path, data)

    async def add_data_definition(self, uri: str, type: DataDefinitionType) -> bool:
        path = "/data-definition"
        data = {"uri": uri, "type": type}

        return await self._k2_post_request(path, data)

    async def heartbeat(self):
        path = "/heartbeat"
        return await self._k2_get_request(path)

    async def _k2_post_request(self, path, data=None, params=None):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.k2_core_url + path,
                params=params,
                data=data,
                timeout=settings.default_k2_core_timeout,
            )
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            return response.json()

    async def _k2_get_request(self, path):
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.k2_core_url + path)
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            return response.json()

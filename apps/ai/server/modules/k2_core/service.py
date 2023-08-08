import logging

import httpx

from config import dbsettings, settings
from modules.k2_core.models.requests import QuestionRequest
from modules.k2_core.models.responses import NLQueryResponse
from modules.k2_core.repository import K2CoreRepository

logger = logging.getLogger(__name__)


# use request
class K2Service:
    def __init__(self):
        self.repo = K2CoreRepository()

    async def answer_question(self, question: QuestionRequest) -> NLQueryResponse:
        path = "/question"
        data = {"question": question.question, "db_alias": dbsettings.db_alias}

        response: NLQueryResponse = await self._k2_post_request(path, json=data)
        self.repo.record_response_pointer(response["id"])
        return response

    async def heartbeat(self):
        path = "/heartbeat"
        return await self._k2_get_request(path)

    async def _k2_post_request(self, path, data=None, params=None, json=None):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.k2_core_url + path,
                params=params,
                data=data,
                json=json,
                timeout=settings.default_k2_core_timeout,
            )
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            return response.json()

    async def _k2_get_request(self, path):
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.k2_core_url + path)
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            return response.json()

import logging
import re

import httpx
from bson import ObjectId

from config import settings
from modules.k2_core.models.requests import QuestionRequest
from modules.k2_core.models.responses import NLQueryResponse
from modules.k2_core.repository import K2CoreRepository
from modules.organization.models.entities import Organization

logger = logging.getLogger(__name__)


# use request
class K2Service:
    def __init__(self):
        self.repo = K2CoreRepository()

    async def answer_question(
        self, question_request: QuestionRequest, organization: Organization
    ) -> NLQueryResponse:
        path = "/question"
        slack_user_mention_pattern = r"<@(.*?)>"
        slack_team_mention_pattern = r"<!(.*?)>"
        slack_channel_mention_pattern = r"<#(.*?)>"
        question_string = re.sub(
            slack_channel_mention_pattern,
            "",
            re.sub(
                slack_team_mention_pattern,
                "",
                re.sub(slack_user_mention_pattern, "", question_request.question),
            ),
        )

        data = {"question": question_string, "db_alias": organization.db_alias}

        response = await self._k2_post_request(path, json=data)
        # adds document that links user info to query response
        query_response = NLQueryResponse(**response)
        query_response.id = response["id"]
        self.repo.record_response_pointer(
            response["id"], question_request.user, ObjectId(organization.id)
        )
        return query_response

    async def heartbeat(self):
        path = "/heartbeat"
        return await self._k2_get_request(path)

    async def _k2_post_request(self, path, data=None, params=None, json=None):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    settings.k2_core_url + path,
                    params=params,
                    data=data,
                    json=json,
                    timeout=settings.default_k2_core_timeout,
                )
                response.raise_for_status()  # Raise an exception for non-2xx status codes
            except Exception as e:
                raise e

            return response.json()

    async def _k2_get_request(self, path):
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.k2_core_url + path)
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            return response.json()

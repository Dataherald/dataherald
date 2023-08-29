import logging
import re

import httpx
from bson import ObjectId

from config import settings
from modules.k2_core.models.requests import QuestionRequest
from modules.k2_core.models.responses import NLQueryResponse
from modules.k2_core.repository import K2CoreRepository
from modules.organization.models.entities import Organization
from modules.query.service import QueryService

logger = logging.getLogger(__name__)


# use request
class K2Service:
    def __init__(self):
        self.repo = K2CoreRepository()
        self.query_service = QueryService()

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

        # ask question to k2 core
        response = await self._k2_post_request(path, json=data)

        # adds document that links user info to query response
        query_response = NLQueryResponse(**response)
        query_response.id = response["id"]
        query_id: str = response["id"]["$oid"]

        # if query ref doesn't exist, create one
        if not self.query_service.get_query_ref(query_id):
            display_id = self.repo.get_next_display_id(ObjectId(organization.id))

            self.repo.add_query_response_ref(
                ObjectId(query_id),
                ObjectId(organization.id),
                question_request.user,
                display_id,
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

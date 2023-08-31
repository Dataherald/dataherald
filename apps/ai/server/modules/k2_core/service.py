import logging
from datetime import datetime, timezone

import httpx
from bson import ObjectId

from config import settings
from modules.k2_core.models.requests import QuestionRequest
from modules.k2_core.models.responses import NLQueryResponse, NLQuerySlackResponse
from modules.k2_core.repository import K2CoreRepository
from modules.organization.models.entities import Organization
from modules.query.models.entities import QueryRef
from modules.query.service import QueryService
from modules.user.models.entities import SlackInfo
from utils.slack import SlackWebClient, remove_slack_mentions

logger = logging.getLogger(__name__)


# use request
class K2Service:
    def __init__(self):
        self.repo = K2CoreRepository()
        self.query_service = QueryService()

    async def answer_question(
        self, question_request: QuestionRequest, organization: Organization
    ) -> NLQuerySlackResponse:
        path = "/question"
        question_string = remove_slack_mentions(question_request.question)

        data = {"question": question_string, "db_alias": organization.db_alias}

        # ask question to k2 core
        response = await self._k2_post_request(path, json=data)

        # adds document that links user info to query response
        query_response = NLQueryResponse(**response)
        query_id: str = response["id"]["$oid"]

        # if query ref doesn't exist, create one
        if not self.query_service.get_query_ref(query_id):
            display_id = self.repo.get_next_display_id(ObjectId(organization.id))

            current_utc_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            username = SlackWebClient(
                organization.slack_installation.bot.token
            ).get_user_real_name(question_request.slack_user_id)
            query_ref = QueryRef(
                query_response_id=ObjectId(query_id),
                question_date=current_utc_time,
                last_updated=current_utc_time,
                organization_id=ObjectId(organization.id),
                display_id=display_id,
                slack_info=SlackInfo(
                    user_id=question_request.slack_user_id,
                    channel_id=question_request.slack_channel_id,
                    thread_ts=question_request.slack_thread_ts,
                    username=username,
                ),
            )

            self.repo.add_query_response_ref(query_ref.dict(exclude={"id"}))

        if (
            organization.confidence_threshold == 1
            or query_response.confidence_score < organization.confidence_threshold
        ):
            is_above_confidence_threshold = False
        else:
            is_above_confidence_threshold = True

        return NLQuerySlackResponse(
            id=query_id,
            display_id=query_ref.display_id,
            is_above_confidence_threshold=is_above_confidence_threshold,
            **query_response.dict(exclude={"id"})
        )

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

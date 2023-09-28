from datetime import datetime, timezone
from typing import Any, Dict

import httpx
from bson import ObjectId

from config import settings
from modules.golden_sql.models.requests import GoldenSQLRequest
from modules.golden_sql.service import GoldenSQLService
from modules.organization.models.responses import OrganizationResponse
from modules.organization.service import OrganizationService
from modules.query.models.entities import (
    QueryRef,
    QueryStatus,
    Question,
    SQLGenerationStatus,
)
from modules.query.models.requests import (
    QueryExecutionRequest,
    QueryUpdateRequest,
    QuestionRequest,
)
from modules.query.models.responses import (
    CoreQueryResponse,
    QueryListResponse,
    QueryResponse,
    QuerySlackResponse,
)
from modules.query.repository import QueryRepository
from modules.user.models.entities import SlackInfo, User
from modules.user.service import UserService
from utils.exception import raise_for_status
from utils.slack import SlackWebClient, remove_slack_mentions

CONFIDENCE_CAP = 0.95


class QueryService:
    def __init__(self):
        self.repo = QueryRepository()
        self.golden_sql_service = GoldenSQLService()
        self.org_service = OrganizationService()
        self.user_service = UserService()

    async def answer_question(
        self, question_request: QuestionRequest, organization: OrganizationResponse
    ) -> QuerySlackResponse:
        question_string = remove_slack_mentions(question_request.question)

        # ask question to k2 core
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.k2_core_url + "/question",
                json={
                    "question": question_string,
                    "db_connection_id": organization.db_connection_id,
                },
                timeout=settings.default_k2_core_timeout,
            )

            raise_for_status(response.status_code, response.text)

        # adds document that links user info to query response
        query_response = CoreQueryResponse(**response.json())
        query_id: str = response.json()["id"]["$oid"]

        # if query ref doesn't exist, create one
        if not self.repo.get_query_response_ref(query_id):
            display_id = self.repo.get_next_display_id(organization.id)

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

        return QuerySlackResponse(
            id=query_id,
            display_id=query_ref.display_id,
            is_above_confidence_threshold=is_above_confidence_threshold,
            **query_response.dict(exclude={"id"}),
        )

    def get_query(self, query_id: str):
        response_ref = self.repo.get_query_response_ref(query_id)
        query_response = self.repo.get_query_response(query_id)
        question = self.repo.get_question(str(query_response.nl_question_id))
        if question and query_response:
            return self._get_mapped_query_response(
                query_id, response_ref, question, query_response
            )

        return None

    def get_queries(
        self,
        order: str,
        page: int,
        page_size: int,
        ascend: bool,  # noqa: ARG002
        org_id: str,
    ) -> list[QueryListResponse]:
        query_response_refs = self.repo.get_query_response_refs(
            skip=page * page_size, limit=page_size, order=order, org_id=org_id
        )
        query_response_ids = [str(qrr.query_response_id) for qrr in query_response_refs]
        query_responses = self.repo.get_query_responses(query_response_ids)
        questions = self.repo.get_questions(
            [str(r.nl_question_id) for r in query_responses]
        )

        question_dict: Dict[Any, str] = {}
        for q in questions:
            q_id = q.id
            if q_id not in question_dict:
                question_dict[q_id] = q.question

        query_response_dict: Dict[Any, CoreQueryResponse] = {}
        for qr in query_responses:
            query_response_dict[qr.id] = qr

        if query_responses:
            return [
                QueryListResponse(
                    id=str(qrr.query_response_id),
                    username=qrr.slack_info.username or "unknown",
                    question=question_dict[
                        query_response_dict[qrr.query_response_id].nl_question_id
                    ],
                    nl_response=query_response_dict[qrr.query_response_id].nl_response,
                    question_date=qrr.question_date,
                    status=self._get_query_status(
                        str(qrr.query_response_id),
                        query_response_dict[
                            qrr.query_response_id
                        ].sql_generation_status,
                    ),
                    evaluation_score=self._convert_confidence_score(
                        query_response_dict[qrr.query_response_id].confidence_score
                    ),
                    display_id=qrr.display_id,
                )
                for qrr in query_response_refs
            ]

        return []

    async def patch_query(
        self,
        query_id: str,
        query_request: QueryUpdateRequest,
        organization: OrganizationResponse,
        user: User,
    ) -> QueryResponse:
        is_golden_record = (
            True if query_request.query_status == QueryStatus.VERIFIED else False
        )
        # request update query to core
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                settings.k2_core_url + f"/nl-query-responses/{query_id}",
                json={"sql_query": query_request.sql_query},
                timeout=settings.default_k2_core_timeout,
            )
            raise_for_status(response.status_code, response.text)

            new_query_response = CoreQueryResponse(**response.json())
            question = self.repo.get_question(new_query_response.nl_question_id["$oid"])
            new_response_ref = self.repo.get_query_response_ref(query_id)

            # add/delete golden_record
            if is_golden_record:
                golden_sql = GoldenSQLRequest(
                    question=question.question,
                    sql_query=query_request.sql_query,
                    db_connection_id=organization.db_connection_id,
                )
                await self.golden_sql_service.add_verified_query_golden_sql(
                    golden_sql,
                    organization.id,
                    query_id,
                )
            else:
                golden_sql_ref = self.golden_sql_service.get_verified_golden_sql_ref(
                    query_id
                )
                if golden_sql_ref:
                    await self.golden_sql_service.delete_golden_sql(
                        "", query_response_id=query_id
                    )

            current_utc_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            updated_query_response_ref = {
                "last_updated": current_utc_time,
                "updated_by": user.id,
            }
            self.repo.update_last_updated(query_id, updated_query_response_ref)

            # send user verified query on slack
            if is_golden_record:
                SlackWebClient(
                    organization.slack_installation.bot.token
                ).send_verified_query_message(
                    new_response_ref,
                    new_query_response,
                    question.question,
                )

            return self._get_mapped_query_response(
                query_id, new_response_ref, question, new_query_response
            )

    async def run_query(self, query_id: str, query_request: QueryExecutionRequest):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.k2_core_url + "/nl-query-responses",
                json={
                    "query_id": query_id,
                    "sql_query": query_request.sql_query,
                },
                timeout=settings.default_k2_core_timeout,
            )
            raise_for_status(response.status_code, response.text)
            response_ref = self.repo.get_query_response_ref(query_id)
            new_query_response = CoreQueryResponse(**response.json())
            question = self.repo.get_question(new_query_response.nl_question_id["$oid"])
            return self._get_mapped_query_response(
                query_id, response_ref, question, new_query_response
            )

    def get_query_ref(self, query_id: str):
        return self.repo.get_query_response_ref(query_id)

    def _get_mapped_query_response(
        self,
        query_id: str,
        response_ref: QueryRef,
        question: Question,
        query_response: CoreQueryResponse,
    ) -> QueryResponse:
        return QueryResponse(
            id=query_id,
            username=response_ref.slack_info.username or "unknown",
            question=question.question,
            nl_response=query_response.nl_response,
            sql_query=query_response.sql_query,
            sql_query_result=query_response.sql_query_result,
            ai_process=query_response.intermediate_steps,
            question_date=response_ref.question_date,
            last_updated=response_ref.last_updated,
            updated_by=self.user_service.get_user(str(response_ref.updated_by))
            if response_ref.updated_by
            else None,
            status=self._get_query_status(
                query_id, query_response.sql_generation_status
            ),
            evaluation_score=self._convert_confidence_score(
                query_response.confidence_score
            ),
            sql_error_message=query_response.error_message,
            display_id=response_ref.display_id,
        )

    def _get_query_status(
        self, query_id: str, sql_generation_status: SQLGenerationStatus
    ) -> QueryStatus:
        status = QueryStatus.NOT_VERIFIED
        golden_sql = self.golden_sql_service.get_verified_golden_sql_ref(query_id)
        if sql_generation_status == SQLGenerationStatus.VALID and golden_sql:
            status = QueryStatus.VERIFIED
        elif sql_generation_status in {
            SQLGenerationStatus.INVALID,
            SQLGenerationStatus.NONE,
        }:
            status = QueryStatus.SQL_ERROR
        return status

    def _convert_confidence_score(self, confidence_score: float) -> int:
        if confidence_score > CONFIDENCE_CAP:
            return 95
        return int(confidence_score * 100)

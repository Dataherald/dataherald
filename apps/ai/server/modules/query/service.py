from datetime import datetime, timezone
from typing import Dict

import httpx
from bson import ObjectId
from fastapi import status

from config import settings
from modules.golden_sql.models.requests import GoldenSQLRequest
from modules.golden_sql.service import GoldenSQLService
from modules.organization.models.responses import OrganizationResponse
from modules.query.models.entities import (
    BaseEngineAnswer,
    EngineAnswer,
    Query,
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
    EngineAnswerResponse,
    QueryListResponse,
    QueryResponse,
    QuerySlackResponse,
)
from modules.query.repository import QueryRepository
from modules.user.models.entities import SlackInfo
from modules.user.models.responses import UserResponse
from modules.user.service import UserService
from utils.analytics import Analytics
from utils.exception import QueryEngineError, raise_for_status
from utils.slack import SlackWebClient, remove_slack_mentions

CONFIDENCE_CAP = 0.95


class QueryService:
    def __init__(self):
        self.repo = QueryRepository()
        self.golden_sql_service = GoldenSQLService()
        self.user_service = UserService()
        self.analytics = Analytics()

    async def answer_question(
        self, question_request: QuestionRequest, organization: OrganizationResponse
    ) -> QuerySlackResponse:
        question_string = remove_slack_mentions(question_request.question)
        current_utc_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        username = SlackWebClient(
            organization.slack_installation.bot.token
        ).get_user_real_name(question_request.slack_user_id)

        # ask question to k2 engine
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.k2_core_url + "/questions",
                json={
                    "question": question_string,
                    "db_connection_id": organization.db_connection_id,
                },
                timeout=settings.default_k2_core_timeout,
            )
            response_json = response.json()
            if not response_json["question_id"]:
                raise_for_status(response.status_code, response.text)

            answer = EngineAnswerResponse(**response_json)

            query = Query(
                question_id=ObjectId(answer.question_id),
                response_id=ObjectId(answer.id) if answer.id else None,
                question_date=current_utc_time,
                last_updated=current_utc_time,
                organization_id=ObjectId(organization.id),
                display_id=self.repo.get_next_display_id(organization.id),
                slack_info=SlackInfo(
                    user_id=question_request.slack_user_id,
                    channel_id=question_request.slack_channel_id,
                    thread_ts=question_request.slack_thread_ts,
                    username=username,
                ),
                status=QueryStatus.NOT_VERIFIED.value
                if answer.sql_generation_status == SQLGenerationStatus.VALID
                else QueryStatus.SQL_ERROR.value,
            )

            query_id = self.repo.add_query(query.dict(exclude={"id"}))

            self.analytics.track(
                question_request.slack_user_id,
                "query_asked",
                {
                    "query_id": query_id,
                    "display_id": query.display_id,
                    "question_id": str(query.question_id),
                    "response_id": str(query.response_id),
                    "organization_id": organization.id,
                    "status": query.status,
                    "username": username,
                },
            )

            if response.status_code != status.HTTP_201_CREATED:
                raise QueryEngineError(
                    response.status_code,
                    query_id,
                    query.display_id,
                    answer.error_message,
                )

            if (
                organization.confidence_threshold == 1
                or answer.confidence_score < organization.confidence_threshold
            ):
                is_above_confidence_threshold = False
            else:
                is_above_confidence_threshold = True

            return QuerySlackResponse(
                id=query_id,
                display_id=query.display_id,
                is_above_confidence_threshold=is_above_confidence_threshold,
                **answer.dict(exclude={"id"}),
            )

    def get_query(self, query_id: str):
        query = self.repo.get_query(query_id)
        question = self.repo.get_question(str(query.question_id))
        answer = (
            self.repo.get_answer(str(query.response_id)) if query.response_id else None
        )
        if query:
            return self._get_mapped_query_response(query, question, answer)

        return None

    def get_queries(
        self,
        order: str,
        page: int,
        page_size: int,
        ascend: bool,  # noqa: ARG002
        question_id: str,
        org_id: str,
    ) -> list[QueryListResponse]:
        if question_id:
            query = self.repo.get_query_by_question_id(question_id)
            question = self.repo.get_question(str(question_id))
            answers = self.repo.get_question_answers(str(question_id))
            return [
                QueryListResponse(
                    id=str(query.id),
                    username=query.slack_info.username or "unknown",
                    question=question.question,
                    response=query.custom_response
                    or (answer.response if query.response_id else ""),
                    status=query.status,
                    question_date=query.question_date,
                    evaluation_score=self._convert_confidence_score(
                        answer.confidence_score
                    ),
                    display_id=query.display_id,
                )
                for answer in answers
            ]

        queries = self.repo.get_queries(
            skip=page * page_size, limit=page_size, order=order, org_id=org_id
        )

        query_responses = self.repo.get_answers(
            [
                result
                for query in queries
                if (result := str(query.response_id) if query.response_id else None)
                is not None
            ]
        )

        questions = self.repo.get_questions(
            [str(query.question_id) for query in queries]
        )

        question_dict: Dict[ObjectId, str] = {}
        for question in questions:
            if question.id not in question_dict:
                question_dict[question.id] = question.question

        query_response_dict: Dict[ObjectId, EngineAnswer | None] = {}
        for answer in query_responses:
            query_response_dict[answer.id] = answer

        if questions:
            return [
                QueryListResponse(
                    id=str(query.id),
                    username=query.slack_info.username or "unknown",
                    question=question_dict[query.question_id],
                    response=query.custom_response
                    or (
                        query_response_dict[query.response_id].response
                        if query.response_id
                        else ""
                    ),
                    question_date=query.question_date,
                    status=query.status,
                    evaluation_score=self._convert_confidence_score(
                        query_response_dict[query.response_id].confidence_score
                    )
                    if query.response_id
                    else 0,
                    display_id=query.display_id,
                )
                for query in queries
            ]

        return []

    async def patch_response(
        self,
        query_id: str,
        query_request: QueryUpdateRequest,
        organization: OrganizationResponse,
        user: UserResponse,
    ) -> QueryResponse:
        query = self.repo.get_query(query_id)

        if query_request.query_status != QueryStatus.REJECTED:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.k2_core_url + "/responses",
                    json={
                        "question_id": str(query.question_id),
                        "sql_query": query_request.sql_query,
                    },
                    timeout=settings.default_k2_core_timeout,
                )
                raise_for_status(response.status_code, response.text)

                new_query_response = EngineAnswerResponse(**response.json())
        else:
            new_query_response = None

        question = self.repo.get_question(query.question_id)
        current_utc_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        updated_query = {
            "response_id": ObjectId(new_query_response.id)
            if new_query_response
            else None,
            "last_updated": current_utc_time,
            "updated_by": ObjectId(user.id),
            "status": query_request.query_status.value,
            "custom_response": query_request.custom_response,
        }
        self.repo.update_query(str(query.id), updated_query)
        updated_query = self.repo.get_query(str(query.id))

        # verified
        if query_request.query_status == QueryStatus.VERIFIED:
            golden_sql = GoldenSQLRequest(
                question=question.question,
                sql_query=query_request.sql_query,
                db_connection_id=organization.db_connection_id,
            )
            await self.golden_sql_service.add_verified_query_golden_sql(
                golden_sql,
                organization.id,
                updated_query.id,
            )

            SlackWebClient(
                organization.slack_installation.bot.token
            ).send_verified_query_message(
                updated_query,
                new_query_response,
                question.question,
            )
        # rejected or not verified
        else:
            golden_sql_ref = self.golden_sql_service.get_verified_golden_sql_ref(
                updated_query.id
            )
            if golden_sql_ref:
                await self.golden_sql_service.delete_golden_sql(
                    str(golden_sql_ref.golden_sql_id)
                )
            if query_request.query_status == QueryStatus.REJECTED:
                SlackWebClient(
                    organization.slack_installation.bot.token,
                ).send_rejected_query_message(updated_query)

        self.analytics.track(
            user.email,
            "query_saved",
            {
                "query_id": query_id,
                "question_id": str(updated_query.question_id),
                "response_id": str(updated_query.response_id)
                if updated_query.response_id
                else None,
                "organization_id": organization.id,
                "display_id": updated_query.display_id,
                "status": query_request.query_status.value,
                "confidence_score": new_query_response.confidence_score
                if new_query_response
                else None,
            },
        )

        return self._get_mapped_query_response(
            updated_query, question, new_query_response
        )

    async def run_response(
        self, query_id: str, query_request: QueryExecutionRequest, user: UserResponse
    ):
        query = self.repo.get_query(query_id)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.k2_core_url + "/responses",
                json={
                    "question_id": str(query.question_id),
                    "sql_query": query_request.sql_query,
                },
                timeout=settings.default_k2_core_timeout,
            )
            raise_for_status(response.status_code, response.text)
            query.custom_response = None
            question = self.repo.get_question(query.question_id)
            new_query_response = EngineAnswerResponse(**response.json())

            self.analytics.track(
                user.email,
                "query_executed",
                {
                    "query_id": query_id,
                    "question_id": new_query_response.id,
                    "response_id": new_query_response.id,
                    "organization_id": user.organization_id,
                    "sql_generation_status": new_query_response.sql_generation_status.value,
                    "confidence_score": new_query_response.confidence_score,
                },
            )

            return self._get_mapped_query_response(query, question, new_query_response)

    def _get_mapped_query_response(
        self,
        query: Query,
        question: Question,
        answer: BaseEngineAnswer = None,
    ) -> QueryResponse:
        if not answer:
            answer = BaseEngineAnswer(
                response_id=None,
                question_id=query.question_id,
                response=query.custom_response or "",
                sql_query="",
                confidence_score=0,
            )

        return QueryResponse(
            id=str(query.id),
            username=query.slack_info.username or "unknown",
            question=question.question,
            response=query.custom_response or answer.response,
            sql_query=answer.sql_query,
            sql_query_result=answer.sql_query_result,
            ai_process=answer.intermediate_steps or ["process unknown"],
            question_date=query.question_date,
            last_updated=query.last_updated,
            updated_by=self.user_service.get_user(str(query.updated_by))
            if query.updated_by
            else None,
            status=query.status,
            evaluation_score=self._convert_confidence_score(answer.confidence_score),
            sql_error_message=answer.error_message,
            display_id=query.display_id,
        )

    def _convert_confidence_score(self, confidence_score: float) -> int:
        if not confidence_score:
            return 0
        if confidence_score > CONFIDENCE_CAP:
            return 95
        return int(confidence_score * 100)

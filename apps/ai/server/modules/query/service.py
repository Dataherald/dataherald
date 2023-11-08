from datetime import datetime, timezone
from typing import Dict

import httpx
from bson import ObjectId
from fastapi import status

from config import settings
from modules.db_connection.service import DBConnectionService
from modules.golden_sql.models.requests import GoldenSQLRequest
from modules.golden_sql.service import GoldenSQLService
from modules.organization.models.responses import OrganizationResponse
from modules.query.models.entities import (
    Answer,
    Query,
    QueryStatus,
    Question,
    SQLGenerationStatus,
)
from modules.query.models.requests import (
    QueryUpdateRequest,
    QuestionRequest,
    SQLAnswerRequest,
)
from modules.query.models.responses import (
    AnswerResponse,
    MessageResponse,
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
CORRECT_RESPONSE_COUNT = 2
SLACK_CHARACTER_LIMIT = 2700


class QueryService:
    def __init__(self):
        self.repo = QueryRepository()
        self.golden_sql_service = GoldenSQLService()
        self.user_service = UserService()
        self.db_connection_service = DBConnectionService()
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
                settings.engine_url + "/questions",
                json={
                    "question": question_string,
                    "db_connection_id": organization.db_connection_id,
                },
                timeout=settings.default_engine_timeout,
            )
            response_json = response.json()
            if not response_json["question_id"]:
                raise_for_status(response.status_code, response.text)

            answer = AnswerResponse(**response_json)

            query = Query(
                question_id=ObjectId(answer.question_id),
                answer_id=ObjectId(answer.id) if answer.id else None,
                question_date=current_utc_time,
                last_updated=current_utc_time,
                message=answer.response,
                organization_id=ObjectId(organization.id),
                display_id=self.repo.get_next_display_id(organization.id),
                slack_info=SlackInfo(
                    user_id=question_request.slack_user_id,
                    channel_id=question_request.slack_channel_id,
                    thread_ts=question_request.slack_thread_ts,
                    username=username,
                ),
                status=QueryStatus.NOT_VERIFIED
                if answer.sql_generation_status == SQLGenerationStatus.VALID
                else QueryStatus.SQL_ERROR,
            )

            query_id = self.repo.add_query(query.dict(exclude_unset=True))

            self.analytics.track(
                question_request.slack_user_id,
                "query_asked",
                {
                    "query_id": query_id,
                    "display_id": query.display_id,
                    "question_id": str(query.question_id),
                    "answer_id": str(query.answer_id),
                    "organization_id": organization.id,
                    "organization_name": organization.name,
                    "database_name": self.db_connection_service.get_db_connection(
                        organization.db_connection_id
                    ).alias,
                    "confidence_score": answer.confidence_score,
                    "status": query.status,
                    "asker": username,
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
                self.analytics.track(
                    question_request.slack_user_id,
                    "query_correct_on_first_try",
                    {
                        "query_id": query.id,
                        "question_id": str(query.question_id),
                        "response_id": str(query.response_id)
                        if query.response_id
                        else None,
                        "organization_id": organization.id,
                        "organization_name": organization.name,
                        "database_name": self.db_connection_service.get_db_connection(
                            organization.db_connection_id
                        ).alias,
                        "display_id": query.display_id,
                        "status": query.status,
                        "confidence_score": answer.confidence_score,
                        "asker": username,
                    },
                )

            # error handling for response longer than character limit
            if len(answer.response + answer.sql_query) >= SLACK_CHARACTER_LIMIT:
                answer.response = (
                    ":warning: The generated response has been truncated due to exceeding character limit. "
                    + "A full response will be returned once reviewed by the data-team admins: \n\n"
                    + answer.response[
                        : max(SLACK_CHARACTER_LIMIT - len(answer.sql_query), 0)
                    ]
                    + "..."
                )

            return QuerySlackResponse(
                id=query_id,
                display_id=query.display_id,
                is_above_confidence_threshold=is_above_confidence_threshold,
                **answer.dict(exclude={"id"}),
            )

    def get_query(self, query_id: str):
        query = self.repo.get_query(query_id)
        question = self.repo.get_question(str(query.question_id))
        answer = self.repo.get_answer(str(query.answer_id)) if query.answer_id else None
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
                    response=query.message
                    or (answer.response if query.answer_id else ""),
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
                if (result := str(query.answer_id) if query.answer_id else None)
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

        query_response_dict: Dict[ObjectId, Answer | None] = {}
        for answer in query_responses:
            query_response_dict[answer.id] = answer

        if questions:
            return [
                QueryListResponse(
                    id=str(query.id),
                    username=query.slack_info.username or "unknown",
                    question=question_dict[query.question_id],
                    response=query.message
                    or (
                        query_response_dict[query.answer_id].response
                        if query.answer_id
                        else ""
                    ),
                    question_date=query.question_date,
                    status=query.status,
                    evaluation_score=self._convert_confidence_score(
                        query_response_dict[query.answer_id].confidence_score
                    )
                    if query.answer_id
                    else 0,
                    display_id=query.display_id,
                )
                for query in queries
            ]

        return []

    async def update_query(
        self,
        query_id: str,
        query_request: QueryUpdateRequest,
        user: UserResponse,
        organization: OrganizationResponse,
    ) -> QueryResponse:
        query = self.repo.get_query(query_id)
        question = self.repo.get_question(query.question_id)
        answer = self.repo.get_answer(str(query.answer_id)) if query.answer_id else None
        current_utc_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        updated_request = {
            "last_updated": current_utc_time,
            "updated_by": ObjectId(user.id),
        }
        if query_request.query_status:
            updated_request["status"] = query_request.query_status
        if query_request.message:
            updated_request["message"] = query_request.message

        self.repo.update_query(str(query.id), updated_request)
        updated_query = self.repo.get_query(str(query.id))

        # verified
        if query_request.query_status:
            if query_request.query_status == QueryStatus.VERIFIED:
                golden_sql = GoldenSQLRequest(
                    question=question.question,
                    sql_query=answer.sql_query,
                    db_connection_id=organization.db_connection_id,
                )
                await self.golden_sql_service.add_verified_query_golden_sql(
                    golden_sql,
                    organization.id,
                    updated_query.id,
                )

                # logic to track 1st time correct response generated by engine
                all_answers = self.repo.get_answers_by_question_id(
                    str(updated_query.question_id)
                )
                if all(ans.sql_query == answer.sql_query for ans in all_answers):
                    self.analytics.track(
                        user.email,
                        "verified_query_correct_on_first_try",
                        {
                            "query_id": query_id,
                            "question_id": str(updated_query.question_id),
                            "answer_id": str(updated_query.answer_id)
                            if updated_query.answer_id
                            else None,
                            "organization_id": organization.id,
                            "display_id": updated_query.display_id,
                            "status": query_request.query_status,
                            "confidence_score": answer.confidence_score
                            if answer
                            else None,
                            "database_name": self.db_connection_service.get_db_connection(
                                organization.db_connection_id
                            ).alias,
                        },
                    )

            # rejected or not verified
            else:
                golden_sql_ref = self.golden_sql_service.get_verified_golden_sql_ref(
                    updated_query.id
                )
                if golden_sql_ref:
                    await self.golden_sql_service.delete_golden_sql(
                        str(golden_sql_ref.golden_sql_id), query_request.query_status
                    )

        self.analytics.track(
            user.email,
            "query_saved",
            {
                "query_id": query_id,
                "question_id": str(updated_query.question_id),
                "answer_id": str(updated_query.answer_id)
                if updated_query.answer_id
                else None,
                "database_name": self.db_connection_service.get_db_connection(
                    organization.db_connection_id
                ).alias,
                "display_id": updated_query.display_id,
                "status": query_request.query_status,
                "confidence_score": answer.confidence_score if answer else None,
            },
        )

        return self._get_mapped_query_response(updated_query, question, answer)

    async def generate_answer(self, query_id: str, user: UserResponse) -> QueryResponse:
        query = self.repo.get_query(query_id)
        question = self.repo.get_question(str(query.question_id))
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url + "/responses",
                params={"sql_response_only": False, "run_evaluator": True},
                json={"question_id": str(query.question_id)},
                timeout=settings.default_engine_timeout,
            )
            raise_for_status(response.status_code, response.text)
            current_utc_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            answer = AnswerResponse(**response.json())
            updated_request = {
                "last_updated": current_utc_time,
                "updated_by": ObjectId(user.id),
                "answer_id": ObjectId(answer.id),
                "status": QueryStatus.NOT_VERIFIED
                if answer.sql_generation_status == SQLGenerationStatus.VALID
                else QueryStatus.SQL_ERROR,
            }
            self.repo.update_query(str(query.id), updated_request)
            self.analytics.track(
                user.email,
                "query_resubmitted",
                {
                    "query_id": query_id,
                    "question_id": question.id,
                    "answer_id": answer.id,
                    "sql_generation_status": answer.sql_generation_status,
                    "confidence_score": answer.confidence_score,
                    "database_name": self.db_connection_service.get_db_connection(
                        str(question.db_connection_id)
                    ).alias,
                },
            )
            return self._get_mapped_query_response(query, question, answer)

    async def generate_sql_answer(
        self, query_id: str, sql_answer_request: SQLAnswerRequest, user: UserResponse
    ) -> QueryResponse:
        query = self.repo.get_query(query_id)
        question = self.repo.get_question(str(query.question_id))
        if query.status != QueryStatus.NOT_VERIFIED:
            raise_for_status(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="query has already been verified or rejected",
            )
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.engine_url + "/responses",
                params={"sql_response_only": True, "run_evaluator": False},
                json={
                    "question_id": str(query.question_id),
                    "sql_query": sql_answer_request.sql_query,
                },
                timeout=settings.default_engine_timeout,
            )
            raise_for_status(response.status_code, response.text)
            current_utc_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            answer = AnswerResponse(**response.json())
            updated_request = {
                "last_updated": current_utc_time,
                "updated_by": ObjectId(user.id),
                "answer_id": ObjectId(answer.id),
                "status": QueryStatus.NOT_VERIFIED
                if answer.sql_generation_status == SQLGenerationStatus.VALID
                else QueryStatus.SQL_ERROR,
            }

            self.repo.update_query(str(query.id), updated_request)
            self.analytics.track(
                user.email,
                "query_executed",
                {
                    "query_id": query_id,
                    "question_id": question.id,
                    "answer_id": answer.id,
                    "sql_generation_status": answer.sql_generation_status,
                    "confidence_score": answer.confidence_score,
                    "database_name": self.db_connection_service.get_db_connection(
                        str(question.db_connection_id)
                    ).alias,
                },
            )
            return self._get_mapped_query_response(query, question, answer)

    async def generate_message(self, query_id: str) -> MessageResponse:
        query = self.repo.get_query(query_id)
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                settings.engine_url + f"/responses/{str(query.answer_id)}",
                timeout=settings.default_engine_timeout,
            )
            raise_for_status(response.status_code, response.text)

            answer = AnswerResponse(**response.json())
            self.repo.update_query(query_id, {"message": answer.response})
            return MessageResponse(message=answer.response)

    async def send_message(self, query_id: str, organization: OrganizationResponse):
        query = self.repo.get_query(query_id)
        question = self.repo.get_question(str(query.question_id))
        answer = self.repo.get_answer(str(query.answer_id)) if query.answer_id else None

        message = (
            f":wave: Hello, <@{query.slack_info.user_id}>! An Admin has reviewed {query.display_id}.\n\n"
            + f"Question: {question.question}\n\n"
            + f"Response: {query.message or answer.response}\n\n"
            + f":memo: *Generated SQL Query*: \n ```{answer.sql_query}```"
        )

        SlackWebClient(organization.slack_installation.bot.token).send_message(
            query.slack_info.channel_id, query.slack_info.thread_ts, message
        )

    def _get_mapped_query_response(
        self,
        query: Query,
        question: Question,
        answer: Answer = None,
    ) -> QueryResponse:
        if not answer:
            answer = Answer(
                id=None,
                question_id=question.id,
                response=query.message or "",
                sql_query="",
                confidence_score=0,
            )

        return QueryResponse(
            id=str(query.id),
            question_id=str(question.id),
            answer_id=str(answer.id),
            username=query.slack_info.username or "unknown",
            question=question.question,
            response=query.message or answer.response,
            sql_query=answer.sql_query,
            sql_query_result=answer.sql_query_result,
            ai_process=answer.intermediate_steps or ["process unknown"],
            question_date=query.question_date,
            last_updated=query.last_updated,
            updated_by=self.user_service.get_user(
                str(query.updated_by), str(query.organization_id)
            )
            if query.updated_by
            else None,
            status=query.status,
            evaluation_score=self._convert_confidence_score(answer.confidence_score),
            sql_error_message=answer.error_message,
            display_id=query.display_id,
        )

    def _convert_confidence_score(self, confidence_score: float) -> int:
        if not confidence_score:
            return None
        if confidence_score > CONFIDENCE_CAP:
            return 95
        return int(confidence_score * 100)

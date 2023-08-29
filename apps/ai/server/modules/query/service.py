from typing import Any, Dict

import httpx
from bson.objectid import ObjectId

from config import settings
from modules.golden_sql.models.entities import GoldenSQLSource
from modules.golden_sql.models.requests import GoldenSQLRequest
from modules.golden_sql.service import GoldenSQLService
from modules.k2_core.models.entities import SQLGenerationStatus
from modules.k2_core.models.responses import NLQueryResponse
from modules.organization.models.entities import Organization
from modules.organization.service import OrganizationService
from modules.query.models.entities import QueryRef, QueryStatus, Question
from modules.query.models.requests import QueryEditRequest, SQLQueryRequest
from modules.query.models.responses import QueryListResponse, QueryResponse
from modules.query.repository import QueryRepository
from modules.user.models.entities import User
from modules.user.service import UserService


class QueryService:
    def __init__(self):
        self.repo = QueryRepository()
        self.golden_sql_service = GoldenSQLService()
        self.org_service = OrganizationService()
        self.user_service = UserService()

    def get_query(self, query_id: str):
        object_id = ObjectId(query_id)
        response_ref = self.repo.get_query_response_ref(object_id)
        query_response = self.repo.get_query_response(object_id)
        question = self.repo.get_question(query_response.nl_question_id)
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
        org_id: ObjectId,
    ) -> list[QueryListResponse]:
        query_response_refs = self.repo.get_query_response_refs(
            skip=page * page_size, limit=page_size, order=order, org_id=org_id
        )
        object_ids = [qrr.query_response_id for qrr in query_response_refs]
        query_responses = self.repo.get_query_responses(object_ids)
        questions = self.repo.get_questions([r.nl_question_id for r in query_responses])

        question_dict: Dict[Any, str] = {}
        for q in questions:
            q_id = q.id
            if q_id not in question_dict:
                question_dict[q_id] = q.question

        query_response_dict: Dict[Any, NLQueryResponse] = {}
        for qr in query_responses:
            query_response_dict[qr.id] = qr

        if query_responses:
            return [
                QueryListResponse(
                    id=str(qrr.query_response_id),
                    username=qrr.user.username or "unknown",
                    question=question_dict[
                        query_response_dict[qrr.query_response_id].nl_question_id
                    ],
                    nl_response=query_response_dict[qrr.query_response_id].nl_response,
                    question_date=qrr.question_date,
                    status=self._get_query_status(
                        qrr.query_response_id,
                        query_response_dict[
                            qrr.query_response_id
                        ].sql_generation_status,
                    ),
                    evaluation_score=query_response_dict[
                        qrr.query_response_id
                    ].confidence_score
                    * 100,
                )
                for qrr in query_response_refs
            ]

        return []

    async def patch_query(
        self,
        query_id: str,
        query_request: QueryEditRequest,
        organization: Organization,
        user: User,
    ) -> QueryResponse:
        object_id = ObjectId(query_id)
        is_golden_record = (
            True if query_request.query_status == QueryStatus.VERIFIED else False
        )
        # request update query to core
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                settings.k2_core_url + f"/query/{query_id}",
                json={"sql_query": query_request.sql_query},
                timeout=settings.default_k2_core_timeout,
            )
            response.raise_for_status()

            query_response = self.repo.get_query_response(object_id)
            question = self.repo.get_question(query_response.nl_question_id)

            # add/delete golden_record
            if is_golden_record:
                golden_sql = GoldenSQLRequest(
                    question=question.question,
                    sql_query=query_request.sql_query,
                    db_alias=organization.db_alias,
                )
                await self.golden_sql_service.add_golden_sql(
                    golden_sql,
                    str(organization.id),
                    source=GoldenSQLSource.verified_query,
                    query_response_id=query_id,
                )
            else:
                golden_sql_ref = self.golden_sql_service.get_verified_golden_sql_ref(
                    query_id
                )
                if golden_sql_ref:
                    await self.golden_sql_service.delete_golden_sql(
                        "", query_response_id=query_id
                    )

            self.repo.update_last_updated(object_id, user.id)
            response_ref = self.repo.get_query_response_ref(object_id)
            new_query_response = NLQueryResponse(**response.json())
            question = self.repo.get_question(new_query_response.nl_question_id)
            return self._get_mapped_query_response(
                query_id, response_ref, question, new_query_response
            )

    async def run_query(self, query_id: str, query_request: SQLQueryRequest):
        object_id = ObjectId(query_id)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.k2_core_url + f"/query/{query_id}/execution",
                json=query_request.dict(),
                timeout=settings.default_k2_core_timeout,
            )
            response.raise_for_status()
            response_ref = self.repo.get_query_response_ref(object_id)
            new_query_response = NLQueryResponse(**response.json())
            question = self.repo.get_question(new_query_response.nl_question_id)
            return self._get_mapped_query_response(
                query_id, response_ref, question, new_query_response
            )

    def get_query_ref(self, query_id: str):
        return self.repo.get_query_response_ref(ObjectId(query_id))

    def _get_mapped_query_response(
        self,
        query_id: str,
        response_ref: QueryRef,
        question: Question,
        query_response: NLQueryResponse,
    ) -> QueryResponse:
        return QueryResponse(
            id=query_id,
            username=response_ref.user.username or "unknown",
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
            evaluation_score=query_response.confidence_score * 100,
            sql_error_message=query_response.error_message,
        )

    def _get_query_status(
        self, query_id, sql_generation_status: SQLGenerationStatus
    ) -> QueryStatus:
        status = QueryStatus.NOT_VERIFIED
        golden_sql = self.golden_sql_service.get_verified_golden_sql_ref(query_id)
        if sql_generation_status == SQLGenerationStatus.valid and golden_sql:
            status = QueryStatus.VERIFIED
        elif sql_generation_status in {
            SQLGenerationStatus.invalid,
            SQLGenerationStatus.none,
        }:
            status = QueryStatus.SQL_ERROR
        return status

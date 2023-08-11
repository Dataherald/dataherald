from typing import Any, Dict

import httpx
from bson.objectid import ObjectId
from fastapi import HTTPException

from config import settings
from modules.k2_core.models.entities import SQLGenerationStatus
from modules.k2_core.models.responses import NLQueryResponse
from modules.query.models.entities import QueryRef, QueryStatus, Question
from modules.query.models.requests import (
    QueryEditRequest,
    QueryEditRequestCore,
    SQLQueryRequest,
)
from modules.query.models.responses import QueryListResponse, QueryResponse
from modules.query.repository import QueriesRepository


class QueriesService:
    def __init__(self):
        self.repo = QueriesRepository()

    def get_query(self, query_id: str):
        object_id = ObjectId(query_id)
        response_ref = self.repo.get_query_response_ref(object_id)
        query_response = self.repo.get_query_response(object_id)
        question = self.repo.get_question(query_response.nl_question_id)
        if question and query_response:
            return self._get_mapped_query_response(
                query_id, response_ref, question, query_response
            )

        raise HTTPException(status_code=404, detail="query not found")

    def get_queries(
        self,
        order: str,
        page: int,
        page_size: int,
        ascend: bool,  # noqa: ARG002
    ) -> list[QueryListResponse]:
        query_response_refs = self.repo.get_query_response_refs(
            skip=page * page_size, limit=page_size, order=order
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
                    username=qrr.user.username,
                    question=question_dict[
                        query_response_dict[qrr.query_response_id].nl_question_id
                    ],
                    nl_response=query_response_dict[qrr.query_response_id].nl_response,
                    question_date=qrr.question_date,
                    status=self._get_query_status(
                        query_response_dict[
                            qrr.query_response_id
                        ].sql_generation_status,
                        query_response_dict[qrr.query_response_id].golden_record,
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
        self, query_id: str, query_request: QueryEditRequest
    ) -> QueryResponse:
        object_id = ObjectId(query_id)
        golden_record = (
            True if query_request.query_status == QueryStatus.VERIFIED else False
        )
        query_request = QueryEditRequestCore(
            sql_query=query_request.sql_query, golden_record=golden_record
        )
        # request patch query to k2 (repo)
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                settings.k2_core_url + f"/query/{query_id}",
                json=query_request.dict(),
                timeout=settings.default_k2_core_timeout,
            )
            response.raise_for_status()
            self.repo.update_last_updated(object_id)
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

    def _get_mapped_query_response(
        self,
        query_id: str,
        response_ref: QueryRef,
        question: Question,
        query_response: NLQueryResponse,
    ) -> QueryResponse:
        return QueryResponse(
            id=query_id,
            username=response_ref.user.username,
            question=question.question,
            nl_response=query_response.nl_response,
            sql_query=query_response.sql_query,
            sql_query_result=query_response.sql_query_result,
            ai_process=query_response.intermediate_steps,
            question_date=response_ref.question_date,
            last_updated=response_ref.last_updated,
            status=self._get_query_status(
                query_response.sql_generation_status, query_response.golden_record
            ),
            evaluation_score=query_response.confidence_score * 100,
            sql_error_message=query_response.error_message,
        )

    def _get_query_status(
        self, sql_generation_status: SQLGenerationStatus, golden_record: bool
    ) -> QueryStatus:
        status = QueryStatus.NOT_VERIFIED
        if sql_generation_status == SQLGenerationStatus.valid and golden_record:
            status = QueryStatus.VERIFIED
        elif sql_generation_status in {
            SQLGenerationStatus.invalid,
            SQLGenerationStatus.none,
        }:
            status = QueryStatus.SQL_ERROR
        return status

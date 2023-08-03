import httpx
from bson.objectid import ObjectId
from fastapi import HTTPException

from config import settings
from modules.k2_core.models.entities import SQLGenerationStatus
from modules.k2_core.models.responses import NLQueryResponse
from modules.query.models.entities import QueryRef, QueryStatus, Question
from modules.query.models.requests import QueryEditRequest, SQLQueryRequest
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
        order: str,  # noqa: ARG002
        page: int,
        page_size: int,
        ascend: bool,  # noqa: ARG002
    ) -> list[QueryListResponse]:
        # assuming all return objects in order
        response_refs = self.repo.get_query_response_refs(
            skip=page * page_size, limit=page_size
        )
        object_ids = [qrr.query_response_id for qrr in response_refs]
        query_responses = self.repo.get_query_responses(object_ids)
        questions = self.repo.get_questions([r.nl_question_id for r in query_responses])

        if query_responses:
            return [
                QueryListResponse(
                    id=str(object_ids[i]),
                    user=response_refs[i].user,
                    question=questions[i].question,
                    nl_response=query_responses[i].nl_response,
                    question_date=response_refs[i].question_date,
                    status=self._get_query_status(
                        query_responses[i].sql_generation_status,
                        query_responses[i].golden_record,
                    ),
                    evaluation_score=query_responses[i].confidence_level,
                )
                for i in range(len(questions))
            ]
        raise HTTPException(status_code=404, detail="no queries")

    def patch_query(self, query_id: str, data: QueryEditRequest) -> QueryResponse:
        object_id = ObjectId(query_id)

        # request patch query to k2 (repo)
        with httpx.Client() as client:
            response = client.patch(
                settings.k2_core_url + f"/query/{query_id}", data=data.json()
            )
            response.raise_for_status()
            self.repo.update_last_updated(object_id)
            response_ref = self.repo.get_query_response_ref(object_id)
            new_query_response = NLQueryResponse(**response.json())
            question = self.repo.get_question(new_query_response.nl_question_id)
            return self._get_mapped_query_response(
                query_id, response_ref, question, new_query_response
            )

    def run_query(self, query_id: str, sql_query: SQLQueryRequest):
        object_id = ObjectId(query_id)
        with httpx.Client() as client:
            response = client.post(
                settings.k2_core_url + f"/query/{query_id}/execution",
                data=sql_query.json(),
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
            user=response_ref.user,
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
            evaluation_score=query_response.confidence_level,
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

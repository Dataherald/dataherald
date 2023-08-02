import random

from bson.objectid import ObjectId
from fastapi import HTTPException

from modules.queries.models.entities import QueryStatus
from modules.queries.models.responses import QueryResponse
from modules.queries.repository import QueriesRepository


class QueriesService:
    def __init__(self):
        self.repo = QueriesRepository()

    def get_query(self, query_id: str):
        object_id = ObjectId(query_id)
        response_ref = self.repo.get_query_response_ref(object_id)
        response = self.repo.get_query_response(object_id)
        question = self.repo.get_question(response.nl_question_id)
        if question and response:
            return QueryResponse(
                id=query_id,
                user=response_ref.user,
                question=question.question,
                nl_response=response.nl_response,
                sql_query=response.sql_query,
                ai_process=response.intermediate_steps,
                question_date=response_ref.question_date,
                last_updated=response_ref.last_updated,
                status=random.choice(list(QueryStatus)),  # noqa: S311
                evaluation_score=random.randint(0, 100),  # noqa: S311
            )

        raise HTTPException(status_code=404, detail="query not found")

    def get_queries(
        self,
        order: str,  # noqa: ARG002
        page: int,
        page_size: int,
        ascend: bool,  # noqa: ARG002
    ):
        # assuming all return objects in order
        response_refs = self.repo.get_query_response_refs(
            skip=page * page_size, limit=page_size
        )
        object_ids = [qrr.query_response_id for qrr in response_refs]
        responses = self.repo.get_query_responses(object_ids)
        questions = self.repo.get_questions([r.nl_question_id for r in responses])

        if responses:
            return [
                QueryResponse(
                    id=str(object_ids[i]),
                    user=response_refs[i].user,
                    question=questions[i].question,
                    nl_response=responses[i].nl_response,
                    sql_query=responses[i].sql_query,
                    ai_process=responses[i].intermediate_steps,
                    question_date=response_refs[i].question_date,
                    last_updated=response_refs[i].last_updated,
                    status=random.choice(list(QueryStatus)),  # noqa: S311
                    evaluation_score=random.randint(0, 100),  # noqa: S311
                )
                for i in range(len(questions))
            ]
        raise HTTPException(status_code=404, detail="no queries")

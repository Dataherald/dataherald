from pydantic import BaseModel

from modules.query.models.entities import QueryStatus


class QuestionRequest(BaseModel):
    question: str
    slack_user_id: str | None
    slack_workspace_id: str | None
    slack_channel_id: str | None
    slack_thread_ts: str | None


class QueryUpdateRequest(BaseModel):
    sql_query: str
    query_status: QueryStatus | None


class QueryExecutionRequest(BaseModel):
    sql_query: str

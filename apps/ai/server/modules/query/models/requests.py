from pydantic import BaseModel

from modules.query.models.entities import QueryStatus


class QuestionRequest(BaseModel):
    question: str
    slack_user_id: str | None
    slack_workspace_id: str | None
    slack_channel_id: str | None
    slack_thread_ts: str | None


class QueryUpdateRequest(BaseModel):
    query_status: QueryStatus | None
    message: str | None


class SQLAnswerRequest(BaseModel):
    sql_query: str

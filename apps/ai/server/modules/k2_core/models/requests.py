from pydantic import BaseModel


class EvaluationRequest(BaseModel):
    question: str
    golden_sql: str


class QuestionRequest(BaseModel):
    question: str
    slack_user_id: str | None
    slack_workspace_id: str | None
    slack_channel_id: str | None
    slack_thread_ts: str | None

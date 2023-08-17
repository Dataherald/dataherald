from pydantic import BaseModel

from modules.user.models.entities import SlackQuestionUser


class EvaluationRequest(BaseModel):
    question: str
    golden_sql: str


class QuestionRequest(BaseModel):
    question: str
    user: SlackQuestionUser

from pydantic import BaseModel


class EvaluationRequest(BaseModel):
    question: str
    golden_sql: str


class QuestionRequest(BaseModel):
    question: str

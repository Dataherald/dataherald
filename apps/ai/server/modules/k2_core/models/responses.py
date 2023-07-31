from typing import Any

from pydantic import BaseModel, Field, confloat


class NLQueryResponse(BaseModel):
    id: str | None = Field(alias="_id")
    nl_question_id: Any
    nl_response: str | None = None
    intermediate_steps: list[str] | None = None
    sql_query: str
    exec_time: float | None = None
    golden_record: bool = False
    # date_entered: datetime = datetime.now() add this later


class Evaluation(BaseModel):
    id: str | None = Field(alias="_id")
    question_id: str | None = Field(alias="q_id")
    answer_id: str | None = Field(alias="a_id")
    score: confloat(ge=0, le=1) = 0.5

from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from uuid import UUID


class NLQuery(BaseModel):
    id: UUID
    question: str


class NLQueryResponse(BaseModel):
    nl_question_id: UUID
    table_response: List[Dict[str, Any]]
    nl_response: str
    tables_used: List[str]
    sql: str
    exec_time: Optional[float] = None






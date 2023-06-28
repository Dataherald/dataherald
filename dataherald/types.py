from typing import Any, Dict, List, Optional,Union
from pydantic import BaseModel, Field
from bson.objectid import ObjectId

from uuid import UUID


class NLQuery(BaseModel):
    id: Any
    question: str


class NLQueryResponse(BaseModel):
    id: Any 
    nl_question_id: Any
    table_response: List[Dict[str, Any]]
    nl_response: str
    tables_used: List[str]
    sql: str
    exec_time: Optional[float] = None






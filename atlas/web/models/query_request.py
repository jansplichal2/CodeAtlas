from pydantic import BaseModel
from typing import Optional

class QueryRequest(BaseModel):
    service: str
    query: str
    llmProvider: Optional[str] = None
    llmModel: Optional[str] = None
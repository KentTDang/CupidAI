from typing import TypedDict, List, Annotated
from langchain_core.pydantic_v1 import BaseModel
import operator

class AgentState(TypedDict):
    task: str
    lnode: str
    plan: str
    draft: str
    critique: str
    content: List[str]
    queries: List[str]
    revision_number: int
    max_revisions: int
    count: Annotated[int, operator.add]

class Queries(BaseModel):
    queries: List[str]

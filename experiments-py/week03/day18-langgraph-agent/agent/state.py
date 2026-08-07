from typing import TypedDict,List,Dict,Any
from pydantic import BaseModel

class AgentState(BaseModel):
    goal:str
    steps:List[str]
    current_step:str  = None
    observation:str = None
    evaluation:Dict[str, Any] = None
    action:str = None
    tool:str = None
    args:str = None
    answer:str = None
    retry_count:int = 0
    next_step:str = None
    router:Dict[str,Any] = None
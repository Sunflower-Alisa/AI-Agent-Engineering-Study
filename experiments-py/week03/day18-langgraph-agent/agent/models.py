from pydantic import BaseModel
from typing import Literal


class DecisionModel(BaseModel):
    action:str
    tool:str
    args:dict


class RouterDecision(BaseModel):
    route: Literal[
        "tool",
        "planner"
    ]
    reason: str
    tool: str = None
    args: str = None
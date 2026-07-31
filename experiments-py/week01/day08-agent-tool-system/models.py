from pydantic import BaseModel, Field
from typing import Literal, Optional


class Plan(BaseModel):
    goal: str = Field(description="用户目标")
    steps: list[str] = Field(description="执行步骤列表")


class Evaluation(BaseModel):
    success: bool = True
    need_replan: bool = False
    reason: str = ""


class Execution(BaseModel):
    result: str
    issues: str


class Decision(BaseModel):
    action: Literal["continue", "tool", "replan", "finish"]
    tool: Optional[str] = None
    args: Optional[dict] = None
    reason: str = ""

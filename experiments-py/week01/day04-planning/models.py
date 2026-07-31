from pydantic import BaseModel, Field


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

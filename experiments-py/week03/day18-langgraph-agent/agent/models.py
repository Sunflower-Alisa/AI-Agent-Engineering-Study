from pydantic import BaseModel

class DecisionModel(BaseModel):
    action:str
    tool:str
    args:dict
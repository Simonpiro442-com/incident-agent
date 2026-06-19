from pydantic import BaseModel

class PodInvestigation(BaseModel):
    name: str
    restarts: int
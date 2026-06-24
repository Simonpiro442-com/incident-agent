from pydantic import BaseModel

class PodInvestigation(BaseModel):
    name: str
    restarts: int

class InvestigationResponse(
    BaseModel
):
    service: str

    pods: list

    total_restarts: int

    restart_severity: str

    events: list

    event_severity: str

    analysis: dict
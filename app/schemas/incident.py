from pydantic import BaseModel
from datetime import datetime


class IncidentResponse(BaseModel):
    incident_id: str
    status: str
    alert_name: str
    service: str
    severity: str
    created_at: datetime
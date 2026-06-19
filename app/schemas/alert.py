from pydantic import BaseModel
from typing import List, Dict


class AlertItem(BaseModel):
    labels: Dict[str, str]
    annotations: Dict[str, str]


class AlertPayload(BaseModel):
    receiver: str
    status: str
    alerts: List[AlertItem]
import uuid 
from datetime import datetime
from app.schemas.incident import IncidentResponse
from app.db.models import Incident
from app.repositories.incident_repository import IncidentRepository

class IncidentService:
    def __init__(self):
        self.repository = IncidentRepository()


    def create_incident(self, payload, db):
        incident_id = f"inc_{uuid.uuid4().hex[:8]}"

        first_alert = payload.alerts[0]

        alert_name = first_alert.labels.get("alertname")
        service_name = first_alert.labels.get("service")
        severity = first_alert.labels.get("severity")

        incident_record = Incident(
            incident_id = incident_id, 
            alert_name = alert_name, 
            service = service_name, 
            severity = severity, 
            status = "accepted", 
            created_at = datetime.utcnow()
        )

        self.repository.create(db, incident_record)


        return IncidentResponse(
            incident_id=incident_record.incident_id,
            status=incident_record.status,
            alert_name=incident_record.alert_name,
            service=incident_record.service,
            severity=incident_record.severity,
            created_at=incident_record.created_at
        )

    def list_incidents(self, db):
        return self.repository.get_all(db)
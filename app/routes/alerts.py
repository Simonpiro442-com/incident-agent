from fastapi import APIRouter
from app.schemas.alert import AlertPayload
from app.services.incident_service import IncidentService
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.kubernetes.investigation_service import InvestigationService

router = APIRouter()
incident_service = IncidentService()
investigation_service = InvestigationService()

@router.post("/alerts")
async def receive_alert(payload: AlertPayload, db: Session = Depends(get_db)):

    return incident_service.create_incident(
        payload=payload, 
        db=db
    )

@router.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }

# @router.get("/incidents")


@router.get("/investigate/{service_name}")
async def investigate(service_name: str):
    pod_data = (
        investigation_service.get_service_pods(
            service_name
        )
    )
    deployment_data = (
        investigation_service.get_recent_deployment(
            service_name
        )
    )

    finding = None

    if (
        deployment_data.get("deployment_found")
        and deployment_data.get("deployment_age_minutes", 999) < 30
        and pod_data["total_restarts"] > 5
    ):
        finding = (
            "Recent deployment correlates with increased pod restarts"
        )
    return {
        "service": service_name,
        **pod_data,
        **deployment_data,
        "finding": finding
    }


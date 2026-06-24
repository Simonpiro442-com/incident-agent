from fastapi import APIRouter
from app.schemas.alert import AlertPayload
from app.services.incident_service import IncidentService
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.kubernetes.investigation_service import InvestigationService
from app.services.root_cause_service import RootCauseServices
from app.services.correlation_service import (
    CorrelationService
)
from app.monitoring.prometheus_service import(
    PrometheusService
)


from app.services.metrics_service import (
    MetricService
)

prometheus_service = (
    PrometheusService(
        base_url="http://localhost:9090"
    )
)

metrics_service = (
    MetricService(
        prometheus_service
    )
)
router = APIRouter()
incident_service = IncidentService()
investigation_service = InvestigationService()
root_cause_service = RootCauseServices()
correlation_service = CorrelationService()

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


@router.get("/investigate/{namespace}/{service_name}")
async def investigate(namespace: str, service_name: str):
    pod_data = (
        investigation_service.get_service_pods(
            namespace,
            service_name
        )
    )
    deployment_data = (
        investigation_service.get_recent_deployment(
            namespace,
            service_name
        )
    )

    event_data = (
        investigation_service.get_pod_events(
            namespace,
            service_name
        )
    )

    resource_analysis = (
        investigation_service.analyze_pod_resources(
            namespace,
            service_name
        )
    )

    metrics = {
        **metrics_service.get_pod_count(
            namespace
        ),

        **metrics_service.get_memory_usage(
            namespace
        ),

        **metrics_service.get_cpu_usage(
            namespace
        ),

        **metrics_service.get_network_usage(
            namespace
        )
    }

    correlations = (
        correlation_service.correlate(
            pod_data=pod_data,
            deployment_data=deployment_data,
            event_data=event_data,
            resource_analysis=resource_analysis, 
            metrics=metrics
        )
    )

    root_cause = (
        root_cause_service.analyze(
            correlations
        )
    )

    return {
        "service": service_name,
        **pod_data,
        **deployment_data,
        **event_data, 
        "metrics": metrics,
        "resource_analysis":resource_analysis,
        "analysis": root_cause

    }


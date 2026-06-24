from fastapi import APIRouter 
from fastapi import Query 
from datetime import datetime

from app.services.metrics_service import (
    MetricService
)


from app.monitoring.prometheus_service import(
    PrometheusService
)
from app.config.settings import (
    PROMETHEUS_URL
)

router = APIRouter()

prometheus_service = (
    PrometheusService(
        base_url=(
            #"http://prometheus-server.monitoring.svc.cluster.local"
            PROMETHEUS_URL
        )
    )
)



@router.get("/prometheus/query")
async def query_prometheus(promql: str = Query(...)):
    result = (prometheus_service.query_instant(promql))
    return result

@router.get("/prometheus/query-range")
async def query_range(promql: str, start: str, end: str, step: str="30s"):
    result = (prometheus_service.query_range(
        promql=promql, 
        start=datetime.fromisoformat(
            start
        ), 
        end=datetime.fromisoformat(
            end
        ), 
        step=step
    ))
    return result
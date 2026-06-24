import requests
from datetime import datetime 

class PrometheusService:
    def __init__(self, base_url: str):
        self.base_url = (base_url.rstrip("/"))

    def request(self, endpoint: str, params:dict):
        url = (
            f"{self.base_url}"
            f"{endpoint}"
        )

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            payload = response.json()

            if (payload.get("status") != "success"):
                raise Exception(payload)
            return payload

        except requests.exceptions.RequestException as exc:
            raise Exception(f"Prometheus request failed: {exc}")
        
        except Exception as exc: 
            raise Exception(f"Prometheus query failed: {exc}")

    def query_instant(self, promql: str):
        return self.request(
            endpoint="/api/v1/query", 
            params={"query": promql}
        )

    def query_range(self, promql: str, start:datetime, end:datetime, step:str ="30s"):
        return self.request(
            endpoint="/api/v1/query_range",
            params={
                "query": promql,
                "start": start.timestamp(),
                "end": end.timestamp(),
                "step": step
            }
        )

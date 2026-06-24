from app.monitoring.prometheus_service import(
    PrometheusService
)

class MetricService:
    def __init__(self, prometheus_service: PrometheusService):
        self.prometheus = (prometheus_service)
    
    def get_pod_count(self, namespace: str):
        promql = (f'kube_pod_info{{namespace="namespace"}}')
        result = (self.prometheus.query_instant(promql))
        pod_count = len(result["data"]["result"])
        return {
            "pod_count": pod_count
        }

    def get_memory_usage(self, namespace: str):
        promql = (
            f"""
            sum(container_memory_working_set_bytes{{
                namespace="{namespace}"
            }}
            )"""
        )
        result = (self.prometheus.query_instant(promql))
        value = 0 

        if result["data"]["result"]:
            value = float(result["data"]["result"][0]["value"][1])
        return {
            "memory_bytes": value
        }
    
    def get_cpu_usage(self, namespace: str):
        promql = (
            f'''
            sum(
              rate(
                container_cpu_usage_seconds_total{{
                    namespace="{namespace}"
                }}[5m]
                )
            )'''
        )
        result = (self.prometheus.query_instant(promql))
        value = 0
        if result["data"]["result"]:
            value = float(result["data"]["result"][0]["value"][1])
        return {
            "cpu_usage": value
        }
    
    def get_network_usage(self, namespace: str):
        promql=(
            f"""
            sum(
              rate(
                container_network_receive_bytes_total{{
                    namespace="{namespace}"
                    }}[5m]
              )
            )"""
        )
        result = (
            self.prometheus.query_instant(promql)
        )
        value = 0

        if result["data"]["result"]:
            value = float(
                result["data"]["result"][0]["value"][1]
            )
        return {
            "network_bytes_per_second":
              value
        }
        
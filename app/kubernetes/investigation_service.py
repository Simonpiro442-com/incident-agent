from app.kubernetes.client import get_k8s_client

class InvestigationService:
    def get_service_pods(self, service_name: str):

        v1 = get_k8s_client()

        pods = v1.list_pod_for_all_namespaces()

        matching_pods = []
        for pod in pods.items:
            if service_name not in pod.metadata.name:
                continue

                restart_count = 0 

                if pod.status.container_statuses:
                    for container in pod.status.container_statuses:
                        restart_count += container.restart_count

                matching_pods.append(
                    {
                        "name": pod.metadata.name, 
                        "restarts": restart_count
                    }
                )
        total_restarts = sum(
            pod["restarts"]
            for pod in matching_pods
            )
        
        restart_severity = "normal"

        if total_restarts > 20:
            restart_severity = "critical"
        elif total_restarts > 5:
            restart_severity = "warning"

        return {
                "pods": matching_pods,
                "total_restarts": total_restarts,
                "restart_severity": restart_severity
            }
        
    def get_recent_deployment(self, service_name: str):
        clients = get_k8s_client()
        apps = clients["apps"]

        deployments = (
            apps.list_deployment_for_all_namespaces()
        )
        for deployment in deployments.items:
            if service_name not in deployment.metadata.name:
                continue

            deployment_name = deployment.metadata.alert_name
            namespace = deployment.metadata.namespace
            replicas = deployment.spec.replicas

            image = (
                deployment
                .spec
                .template
                .spec
                .containers 
                .image
            )

            created_at = (
                deployment.metadata.creation_timestamp
            )

            now = datetime.now(timezone.utc)
            deployment_age_minutes = round(
                (
                    now - created_at
                ).tota_seconds() / 60, 
                1
            )

            return {
                "deployment_found": True,
                "deployment_name": deployment_name,
                "namespace": namespace,
                "replicas": replicas,
                "image": image,
                "deployment_age_minutes": deployment_age_minutes
            }
        return {
            "deployment_found": False
        }

                
                


                                        
                    
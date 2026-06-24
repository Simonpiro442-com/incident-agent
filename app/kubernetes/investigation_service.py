from app.kubernetes.client import get_k8s_client

class InvestigationService:
    def get_service_pods(self,namespace: str, service_name: str):

        clients = get_k8s_client()
        v1 = clients["core"]

        pods = v1.list_namespaced_pod(
            namespace=namespace,
            label_selector=f"app={service_name}"
        )

        matching_pods = []
        for pod in pods.items:
            if not self._matches_service(
                pod.metadata.labels,
                service_name
            ):
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
        
    def get_recent_deployment(self,namespace:str, service_name: str):
        clients = get_k8s_client()
        apps = clients["apps"]

        deployments = (
            apps.list_namespaced_deployment(
                namespace=namespace,
                label_selector=f"app={service_name}"
            )
        )
        for deployment in deployments.items:
            if not self._matches_service(
                deployment.metadata.labels,
                service_name
            ):
              continue

            deployment_name = deployment.metadata.name
            namespace = deployment.metadata.namespace
            replicas = deployment.spec.replicas

            image = (
                deployment
                .spec
                .template
                .spec
                .containers[0]
                .image
            )

            created_at = (
                deployment.metadata.creation_timestamp
            )

            now = datetime.now(timezone.utc)
            deployment_age_minutes = round(
                (
                    now - created_at
                ).total_seconds() / 60, 
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
    
    def _matches_service(self, labels, service_name):
        if not labels:
            return False
        return (
            labels.get("app") == service_name 
            or labels.get("app.kubernetes.io/name") == service_name
        )

    def get_label_selector(self, service_name):
        return f"app={service_name}"
        
        label_selector = self.get_label_selector(
            service_name
        )
        pods = v1.list_namespaced_pod(
            namespace=namespace,
            label_selector=label_selector
        )
        deployments = (
            apps.list_deployment_for_all_namespaces(
                label_selector=label_selector
        )
    )

    def get_pod_events(self,namespace: str, service_name:str):

        clients = get_k8s_client()
        v1 = clients["core"]

        label_selector = f"app={service_name}"

        pods = v1.list_namespaced_pod(
            namespace=namespace,
            label_selector=label_selector
        )
        
        critical_reasons = {
            "BackOff",
            "Failed", 
            "OOMKilled",
            "FailedScheduling"
        }

        collected_events = []
        event_severity = "normal"

        for pod in pods.items:
            events = v1.list_namespaced_event(
                namespace=pod.metadata.namespace
            )

            for event in events.items:
                if (
                    event.involved_object.kind == "Pod"
                    and event.involved_object.name
                    == pod.metadata.name
                ):
                  collected_events.append(
                    {
                        "reason":event.reason, 
                        "message": event.message
                    }
                  )
                  if event.reason in critical_reasons:
                    event_severity = critical
        return {
            "events": collected_events, 
            "event_severity": event_severity
        }

    def analyze_pod_resources(self,namespace: str, service_name: str):
        label_selector = f"app={service_name}"
        clients = get_k8s_client()
        v1 = clients["core"]

        pods = v1.list_namespaced_pod(
            namespace=namespace,
            label_selector=label_selector
        )
        results = []

        for pod in pods.items:
            pod_info = {
                "name": pod.metadata.name, 

                "namespace": (
                    pod.metadata.namespace
                ), 

                "phase": (
                    pod.status.phase
                    ),

                "node": (
                    pod.spec.node_name
                ), 
                
                "pod_ip": (
                    pod.status.pod_ip
                ),

                "start_time": (
                    pod.status.start_time.isoformat()
                    if pod.status.start_time
                    else None
                )
            }

            if pod.status.container_statuses: 
                container = (
                    pod.status.container_statuses[0]
                )

                if container.state.running:
                    pod_info["container_state"] = "running"
                elif container.state.waiting:
                    pod_info["container_state"] = "waiting"
                    pod_info["waiting_reason"] = (container.state.waiting.reason)
                elif container.state.terminated:
                    pod_info["container_state"] = "terminated"
                    pod_info["termination_reason"] = (container.state.terminated.reason)

                if (container.last_state and container.last_state.terminated):
                    pod_info["last_termination_reason"] = (
                        container
                        .last_state
                        .terminated
                        .reason
                    )
                    pod_info["exit_code"] = (
                        container
                        .last_state
                        .terminated
                        .exit_code
                    )
            container_spec = (
                pod.spec.containers[0]
            )
            resources = (
                container_spec.resources
            )
            pod_info["requests"] = (
                resources.requests or {}
            )
            pod_info["limits"] = (
                resources.limits or {}
            )
            results.append(
                pod_info
            )
        return results


                
                


                                        
                    
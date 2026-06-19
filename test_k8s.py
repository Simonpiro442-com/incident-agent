from app.kubernetes.client import get_k8s_client

v1 = get_k8s_client()

pods = v1.list_pod_for_all_namespaces()

print(len(pods.items))
from kubernetes import config 
from kubernetes import client 


def get_k8s_client():
    config.load_kube_config()

    return {
        "core": client.CoreV1Api(),
        "apps": client.AppsV1Api()
    }
MAX_ALLOWED_MEMORY_GI = 4


def get_pod_diagnostics(pod_name: str, namespace: str = "prod") -> dict[str, str]:
    print(f"[Tool: get_pod_diagnostics] Fetching telemetry for {namespace}/{pod_name}")
    return {
        "pod_name": pod_name,
        "namespace": namespace,
        "status": "OOMKilled (Exit Code 137)",
        "current_memory_limit": "1Gi",
        "peak_memory_usage": "1023Mi",
        "last_logs": "FATAL: Java heap space / Worker process 42 killed by cgroup OOM killer (limit 1Gi).",
    }


def apply_memory_patch(pod_name: str, namespace: str, new_limit_gi: int) -> str:
    if new_limit_gi > MAX_ALLOWED_MEMORY_GI:
        raise PermissionError(
            f"Requested memory limit ({new_limit_gi}Gi) exceeds maximum policy limit ({MAX_ALLOWED_MEMORY_GI}Gi)."
        )

    print(
        f"[Tool: apply_memory_patch] Executing: "
        f"kubectl set resources pod/{pod_name} -n {namespace} --limits=memory={new_limit_gi}Gi"
    )
    return f"Successfully updated memory limit for {namespace}/{pod_name} from 1Gi to {new_limit_gi}Gi."

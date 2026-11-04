# RUNBOOK-002: Kubernetes Pod CrashLoopBackOff

## Symptoms
The pod remains in `CrashLoopBackOff` status and the `RESTARTS` counter keeps increasing.

## CloudCorp Diagnostic Procedure
1. Inspect pod events: `kubectl describe pod <pod-name> -n <namespace>`.
2. Verify KeyVault secret mounts and check whether the `/healthz` readiness probe responds on port `8080`.

## Remediation Policy
- If the failure was introduced by a recent configuration deployment, roll back immediately: `kubectl rollout undo deployment/<deployment-name> -n <namespace>`.

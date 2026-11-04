# RUNBOOK-001: Kubernetes Pod OOMKilled (Exit Code 137)

## Symptoms
The pod restarts repeatedly with status `OOMKilled` and exit code `137`.

## CloudCorp Diagnostic Procedure
1. Check current memory usage: `kubectl top pod <pod-name> -n <namespace>`.
2. Inspect previous container logs before termination: `kubectl logs <pod-name> --previous --tail=50 -n <namespace>`.

## Remediation Policy
- You may increase `resources.limits.memory` up to a maximum of `4Gi` without additional approval.
- If a workload requires more than `4Gi` of RAM, STOP and request approval from Platform Engineering in `#sre-war-room`.

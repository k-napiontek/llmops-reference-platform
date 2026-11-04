# RUNBOOK-003: Azure AI Foundry HTTP 429 Too Many Requests (Rate Limit)

## Symptoms
The application or LiteLLM gateway returns `HTTP 429` or `RateLimitError` when calling `gpt-5.4-mini`.

## CloudCorp Diagnostic Procedure
1. Check LiteLLM logs to confirm whether automatic failover to `cloudops-fallback` was triggered.
2. Inspect the current `sku.capacity` (TPM) allocation in `infra/main.tf`.

## Remediation Policy
- Never modify the TPM slider manually in the Azure Portal (ClickOps is strictly prohibited).
- Increase `sku.capacity` in `infra/main.tf` (up to `100`, i.e., 100K TPM) and apply changes via `terraform -chdir=infra apply`.

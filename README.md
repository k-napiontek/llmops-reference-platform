# LLMOps Reference Platform: CloudOps Incident Copilot

A containerized SRE/CloudOps Incident Copilot combining **Azure AI Foundry**, **LiteLLM Proxy**, **HuggingFace Embeddings**, and **LangGraph**.

> 📖 **Pełny przewodnik architektoniczny po polsku:** [docs/ARCHITEKTURA_I_PRZEWODNIK_LLMOPS.md](docs/ARCHITEKTURA_I_PRZEWODNIK_LLMOPS.md)

## Architecture

- **Infrastructure (`infra/`)**: Terraform configuration provisioning Azure AI Foundry (`AIServices`) and the `gpt-5.4-mini` (`GlobalStandard`) deployment.
- **AI Gateway (`gateway/`)**: LiteLLM Proxy container providing a unified OpenAI-compatible endpoint (`cloudops-llm`), parameter normalization (`drop_params: true`), retries, and failover to HuggingFace Serverless Inference (`cloudops-fallback`).
- **Local Vector Retrieval (`agent/retriever.py`, `data/runbooks/`)**: Local semantic search over Markdown SRE runbooks powered by HuggingFace `BAAI/bge-small-en-v1.5` with offline volume caching (`HF_HUB_OFFLINE=1`).
- **Agent State Machine (`agent/graph.py`, `agent/nodes/`, `agent/tools/`)**: LangGraph workflow with conditional routing, read-only diagnostics, state persistence (`MemorySaver`), and a Human-in-the-Loop approval gate (`interrupt_before=["execute_remediation"]`).

## Quick Start

1. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
2. Provision Azure AI Foundry resources:
   ```bash
   export ARM_SUBSCRIPTION_ID=$(az account show --query id -o tsv)
   terraform -chdir=infra init
   terraform -chdir=infra apply
   ```
3. Sync local dependencies and cache the HuggingFace embedding model:
   ```bash
   uv sync
   uv run python -m agent.retriever
   ```
4. Start the LiteLLM gateway and run the containerized agent:
   ```bash
   set -a && source .env && set +a
   docker compose up -d litellm
   docker compose build agent
   docker compose run --rm agent
   ```

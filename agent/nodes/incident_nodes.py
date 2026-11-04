import os
from typing import Literal, TypedDict

from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from agent.retriever import RunbookRetriever
from agent.tools.k8s_tools import apply_memory_patch, get_pod_diagnostics


class IncidentState(TypedDict):
    query: str
    pod_name: str
    namespace: str
    category: str
    runbook_name: str
    runbook_content: str
    diagnostics: dict[str, str]
    proposed_memory_gi: int
    response: str
    execution_result: str


llm = ChatOpenAI(
    model="cloudops-llm",
    base_url=os.getenv("LITELLM_PROXY_URL", "http://localhost:4000/v1"),
    api_key=os.getenv("LITELLM_MASTER_KEY"),
    max_tokens=600,
)

retriever = RunbookRetriever()


def triage_node(state: IncidentState) -> dict[str, str]:
    print("\n[Node: triage] Classifying request via LiteLLM Gateway...")
    msg = llm.invoke([
        SystemMessage(
            content=(
                "Classify the user request. Reply with a single word: "
                "INCIDENT (for infrastructure errors, outages, or troubleshooting) "
                "or GENERAL (for general technical questions)."
            )
        ),
        HumanMessage(content=state["query"]),
    ])
    category = "INCIDENT" if "INCIDENT" in msg.content.strip().upper() else "GENERAL"
    print(f"  -> Category: {category}")
    return {"category": category}


def collect_diagnostics_node(state: IncidentState) -> dict:
    print("[Node: collect_diagnostics] Retrieving runbook and pod telemetry...")
    hit = retriever.search(state["query"], top_k=1)[0]
    diagnostics = get_pod_diagnostics(
        pod_name=state.get("pod_name", "payment-service-7f8b9"),
        namespace=state.get("namespace", "prod"),
    )
    return {
        "runbook_name": hit["filename"],
        "runbook_content": hit["content"],
        "diagnostics": diagnostics,
    }


def propose_remediation_node(state: IncidentState) -> dict:
    print("[Node: propose_remediation] Generating diagnosis and remediation plan...")
    prompt = (
        "You are a Senior SRE Copilot at CloudCorp. Analyze the pod telemetry and internal runbook below.\n"
        f"POD TELEMETRY: {state['diagnostics']}\n"
        f"RUNBOOK ({state['runbook_name']}):\n{state['runbook_content']}\n\n"
        "Provide a concise 3-sentence diagnosis and propose increasing the memory limit to a safe value of 2Gi "
        "(in compliance with the <= 4Gi runbook policy)."
    )
    msg = llm.invoke([SystemMessage(content=prompt), HumanMessage(content=state["query"])])
    return {
        "response": msg.content,
        "proposed_memory_gi": 2,
    }


def execute_remediation_node(state: IncidentState) -> dict[str, str]:
    print("[Node: execute_remediation] Applying approved cluster remediation...")
    result = apply_memory_patch(
        pod_name=state.get("pod_name", "payment-service-7f8b9"),
        namespace=state.get("namespace", "prod"),
        new_limit_gi=state["proposed_memory_gi"],
    )
    return {"execution_result": result}


def general_reply_node(state: IncidentState) -> dict[str, str]:
    print("[Node: general_reply] Answering general inquiry...")
    msg = llm.invoke([
        SystemMessage(content="You are a Senior DevOps Mentor. Provide a concise answer in up to 3 sentences."),
        HumanMessage(content=state["query"]),
    ])
    return {"response": msg.content}


def route_after_triage(state: IncidentState) -> Literal["collect_diagnostics", "general_reply"]:
    return "collect_diagnostics" if state["category"] == "INCIDENT" else "general_reply"

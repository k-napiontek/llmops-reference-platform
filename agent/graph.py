import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from agent.nodes.incident_nodes import (
    IncidentState,
    collect_diagnostics_node,
    execute_remediation_node,
    general_reply_node,
    propose_remediation_node,
    route_after_triage,
    triage_node,
)

builder = StateGraph(IncidentState)

builder.add_node("triage", triage_node)
builder.add_node("collect_diagnostics", collect_diagnostics_node)
builder.add_node("propose_remediation", propose_remediation_node)
builder.add_node("execute_remediation", execute_remediation_node)
builder.add_node("general_reply", general_reply_node)

builder.add_edge(START, "triage")
builder.add_conditional_edges("triage", route_after_triage)
builder.add_edge("collect_diagnostics", "propose_remediation")
builder.add_edge("propose_remediation", "execute_remediation")
builder.add_edge("execute_remediation", END)
builder.add_edge("general_reply", END)

checkpointer = MemorySaver()
copilot_graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["execute_remediation"],
)


def main() -> None:
    thread_config = {"configurable": {"thread_id": "INC-2026-042"}}

    print("=" * 75)
    print("STAGE 1: Starting incident workflow (halts before cluster mutation)")
    print("=" * 75)
    initial_state = copilot_graph.invoke(
        {
            "query": (
                "Pod payment-service-7f8b9 in namespace prod is crashing with OOMKilled (exit code 137). "
                "Diagnose and remediate the issue."
            ),
            "pod_name": "payment-service-7f8b9",
            "namespace": "prod",
        },
        config=thread_config,
    )

    snapshot = copilot_graph.get_state(thread_config)
    print(f"\n[Agent Diagnosis & Plan]:\n{initial_state['response']}")
    print("-" * 75)
    print(f"GRAPH STATUS: Paused before node: {snapshot.next}")
    print(
        f"Pending action: Update memory limit for {initial_state['namespace']}/{initial_state['pod_name']} "
        f"to {initial_state['proposed_memory_gi']}Gi"
    )
    print("-" * 75)

    approval = input("Approve cluster modification? (type 'yes' to execute): ").strip().lower()

    if approval == "yes":
        print("\nResuming workflow from checkpoint (thread_id=INC-2026-042)...")
        final_state = copilot_graph.invoke(None, config=thread_config)
        print(f"EXECUTION RESULT: {final_state['execution_result']}")
    else:
        print("\nAction aborted by operator. No changes applied to the cluster.")


if __name__ == "__main__":
    main()

"""
LangGraph Conditional Routing Logic
====================================
Defines conditional transition rules as specified in Section 8 of Target Architecture.
"""

from ai.graph.state import AgentState

MAX_GENERATION_ATTEMPTS = 3
MAX_HEALING_ATTEMPTS = 2


def route_after_validation(state: AgentState) -> str:
    ast_ok = state.get("ast_valid", False)
    pom_ok = state.get("pom_valid", False)
    sec_ok = state.get("security_valid", False)
    attempts = state.get("generation_attempts", 1)

    if ast_ok and pom_ok and sec_ok:
        return "evaluator"
    if attempts >= MAX_GENERATION_ATTEMPTS:
        return "human_review"
    return "generator"


def route_after_evaluation(state: AgentState) -> str:
    approved = state.get("final_decision") == "APPROVED"
    attempts = state.get("generation_attempts", 1)

    if approved:
        return "sandbox_execution"
    if attempts >= MAX_GENERATION_ATTEMPTS:
        return "human_review"
    return "generator"


def route_after_execution(state: AgentState) -> str:
    status = state.get("execution_status", "")
    attempts = state.get("healing_attempts", 0)

    if status == "PASS":
        return "approved_end"
    if attempts >= MAX_HEALING_ATTEMPTS:
        return "human_review"
    return "failure_classifier"

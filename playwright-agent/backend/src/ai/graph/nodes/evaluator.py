"""
LangGraph Node: Evaluator
=========================
Executes DeepEval quality gate evaluation on state.
"""

from ai.graph.state import AgentState
from ai.evaluation.evaluator import DeepEvalEngine


def evaluator_node(state: AgentState, symbol_registry: dict = None) -> AgentState:
    eval_engine = DeepEvalEngine()
    res = eval_engine.evaluate_script(
        python_script=state.get("generated_script", ""),
        user_story=state.get("user_story", ""),
        acceptance_criteria=state.get("acceptance_criteria", []),
        ast_valid=state.get("ast_valid", False),
        pom_valid=state.get("pom_valid", False),
        security_valid=state.get("security_valid", False),
        retrieved_context=state.get("retrieved_context", []),
        symbol_registry=symbol_registry or {}
    )

    state["evaluation_score"] = res["overall_score"]
    state["evaluation_results"] = res
    state["final_decision"] = res["decision"]
    if not res["approved"]:
        state.get("evaluation_feedback", []).extend(res["feedback"])

    return state

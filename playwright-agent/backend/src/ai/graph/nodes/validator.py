"""
LangGraph Node: Validator
=========================
Executes AST, POM, Symbol, and Security deterministic validators on the generated script.
"""

from ai.graph.state import AgentState
from ai.validation.ast_validator import ASTValidator
from ai.validation.pom_validator import POMValidator
from ai.validation.security_validator import SecurityValidator


def validator_node(state: AgentState, symbol_registry: dict = None) -> AgentState:
    symbol_registry = symbol_registry or {}
    script = state.get("generated_script", "")

    ast_val = ASTValidator()
    pom_val = POMValidator(symbol_registry)
    sec_val = SecurityValidator()

    ast_ok, ast_errs = ast_val.validate(script)
    pom_ok, pom_errs = pom_val.validate(script)
    sec_ok, sec_errs = sec_val.validate(script)

    state["ast_valid"] = ast_ok
    state["pom_valid"] = pom_ok
    state["security_valid"] = sec_ok

    feedback = []
    if not ast_ok: feedback.extend(ast_errs)
    if not pom_ok: feedback.extend(pom_errs)
    if not sec_ok: feedback.extend(sec_errs)

    state["evaluation_feedback"] = feedback
    return state

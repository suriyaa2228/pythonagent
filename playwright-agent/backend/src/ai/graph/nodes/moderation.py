"""
LangGraph Node: Moderation
==========================
Validates user input against prompt injection, secrets, or toxic content.
"""

from ai.graph.state import AgentState
from moderation.moderator import InputModerator


def moderation_node(state: AgentState) -> AgentState:
    moderator = InputModerator()
    user_story = state.get("user_story", "")
    acs = state.get("acceptance_criteria", [])

    is_safe, reason = moderator.moderate_text(f"{user_story} {' '.join(acs)}")
    if not is_safe:
        state["final_decision"] = "REJECTED_MODERATION"
        state["evaluation_feedback"] = [f"Input moderation failed: {reason}"]

    return state

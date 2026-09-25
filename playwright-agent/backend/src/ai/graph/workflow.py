"""
LangGraph Test Generation Control Plane Workflow
================================================
Constructs the primary AI control plane workflow graph using LangGraph as specified in Section 8.
"""

from typing import Dict, Any
from ai.graph.state import AgentState
from ai.graph.nodes.moderation import moderation_node
from ai.graph.nodes.requirement_analyzer import requirement_analyzer_node
from ai.graph.nodes.validator import validator_node
from ai.graph.nodes.evaluator import evaluator_node
from ai.graph.routing import route_after_validation, route_after_evaluation


class TestGenerationWorkflow:
    def __init__(self, orchestrator: Any, symbol_registry: Dict[str, Any] = None):
        self.orchestrator = orchestrator
        self.symbol_registry = symbol_registry or {}

    def run(self, user_story: str, acceptance_criteria: list, project: str = "playwright", environment: str = "stage") -> AgentState:
        # Initialize LangGraph AgentState
        state: AgentState = {
            "request_id": f"REQ-{hash(user_story) % 100000}",
            "user_story": user_story,
            "acceptance_criteria": acceptance_criteria,
            "generation_attempts": 0,
            "healing_attempts": 0,
            "retrieved_context": [],
            "retrieved_symbols": [],
            "retrieved_patterns": []
        }

        # 1. Moderation Node
        state = moderation_node(state)
        if state.get("final_decision") == "REJECTED_MODERATION":
            return state

        # 2. Requirement Analyzer Node
        state = requirement_analyzer_node(state)

        # 3. Generation Loop
        while state["generation_attempts"] < 3:
            state["generation_attempts"] += 1

            # Call generator engine
            gen_res = self.orchestrator.generate_test_script(
                user_story=user_story,
                acceptance_criteria=acceptance_criteria,
                project=project,
                environment=environment
            )
            state["generated_script"] = gen_res.get("pythonScript", "")

            # 4. Validator Node
            state = validator_node(state, self.symbol_registry)
            next_step = route_after_validation(state)

            if next_step == "evaluator":
                # 5. Evaluator Node
                state = evaluator_node(state, self.symbol_registry)
                eval_step = route_after_evaluation(state)
                if eval_step in ("sandbox_execution", "approved_end"):
                    state["final_decision"] = "APPROVED"
                    return state

        state["final_decision"] = "HUMAN_REVIEW"
        return state

"""
DeepEval Evaluation Engine
==========================
Main evaluation interface combining DeepEval capabilities and deterministic metric evaluation.
"""

from typing import Dict, Any, List
from ai.evaluation.metrics import QualityMetricsCalculator
from ai.evaluation.thresholds import QualityGatePolicy


class DeepEvalEngine:
    def __init__(self):
        self.calculator = QualityMetricsCalculator()
        self.policy = QualityGatePolicy()

    def evaluate_script(
        self,
        python_script: str,
        user_story: str,
        acceptance_criteria: List[str],
        ast_valid: bool = True,
        pom_valid: bool = True,
        security_valid: bool = True,
        retrieved_context: List[Dict[str, Any]] = None,
        symbol_registry: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        retrieved_context = retrieved_context or []
        symbol_registry = symbol_registry or {}

        # 1. Calculate Metrics
        metrics = self.calculator.calculate_all(
            python_script=python_script,
            user_story=user_story,
            acceptance_criteria=acceptance_criteria,
            retrieved_context=retrieved_context,
            symbol_registry=symbol_registry
        )

        # 2. Evaluate Quality Gate Policy
        gate_result = self.policy.evaluate_gate(
            ast_valid=ast_valid,
            pom_valid=pom_valid,
            security_valid=security_valid,
            metrics=metrics
        )

        return {
            "overall_score": gate_result["overall_score"],
            "approved": gate_result["approved"],
            "decision": "APPROVED" if gate_result["approved"] else "REJECTED",
            "deterministic_pass": gate_result["deterministic_pass"],
            "semantic_pass": gate_result["semantic_pass"],
            "metrics": metrics,
            "feedback": gate_result["feedback"]
        }

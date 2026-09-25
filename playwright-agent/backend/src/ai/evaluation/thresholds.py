"""
Evaluation Thresholds & Hard Quality Gate Policy
=================================================
Defines pass/fail thresholds and quality decision policy specified in Section 17.
"""

from typing import Dict, Any


class QualityGatePolicy:
    MIN_GROUNDING_ACCURACY = 0.90
    MIN_REQUIREMENT_COVERAGE = 0.85
    MIN_OVERALL_SCORE = 0.80

    def evaluate_gate(
        self,
        ast_valid: bool,
        pom_valid: bool,
        security_valid: bool,
        metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        req_cov = metrics.get("requirement_coverage", 0.0)
        grounding = metrics.get("grounding_accuracy", 0.0)
        overall_score = sum(metrics.values()) / max(len(metrics), 1)

        deterministic_pass = ast_valid and pom_valid and security_valid
        semantic_pass = (
            grounding >= self.MIN_GROUNDING_ACCURACY and
            req_cov >= self.MIN_REQUIREMENT_COVERAGE and
            overall_score >= self.MIN_OVERALL_SCORE
        )

        approved = deterministic_pass and semantic_pass

        feedback = []
        if not ast_valid:
            feedback.append("AST Validation Failed: Python syntax error or forbidden AST node detected.")
        if not pom_valid:
            feedback.append("POM Validation Failed: Referenced page method or class does not exist in framework.")
        if not security_valid:
            feedback.append("Security Validation Failed: Potential secret or hardcoded credential detected.")
        if grounding < self.MIN_GROUNDING_ACCURACY:
            feedback.append(f"Grounding score ({grounding}) below minimum threshold ({self.MIN_GROUNDING_ACCURACY}).")
        if req_cov < self.MIN_REQUIREMENT_COVERAGE:
            feedback.append(f"Requirement coverage score ({req_cov}) below threshold ({self.MIN_REQUIREMENT_COVERAGE}).")

        return {
            "approved": approved,
            "overall_score": round(overall_score, 2),
            "deterministic_pass": deterministic_pass,
            "semantic_pass": semantic_pass,
            "metrics": metrics,
            "feedback": feedback
        }

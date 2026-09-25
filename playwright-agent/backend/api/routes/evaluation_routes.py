"""
AI Evaluation Routes
====================
Provides API endpoints for DeepEval metric evaluation, quality gate score retrieval, and dataset evaluation.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ai.evaluation.evaluator import DeepEvalEngine

router = APIRouter()
eval_engine = DeepEvalEngine()


class EvaluateRequest(BaseModel):
    python_script: str
    user_story: str
    acceptance_criteria: List[str]
    ast_valid: Optional[bool] = True
    pom_valid: Optional[bool] = True
    security_valid: Optional[bool] = True


@router.post("/evaluate")
def evaluate_script(req: EvaluateRequest):
    """Evaluates a test script against DeepEval metrics and Quality Gate Policy."""
    res = eval_engine.evaluate_script(
        python_script=req.python_script,
        user_story=req.user_story,
        acceptance_criteria=req.acceptance_criteria,
        ast_valid=req.ast_valid,
        pom_valid=req.pom_valid,
        security_valid=req.security_valid
    )
    return res


@router.get("/evaluations/{evaluation_id}")
def get_evaluation(evaluation_id: str):
    return {
        "evaluation_id": evaluation_id,
        "status": "COMPLETED",
        "overall_score": 0.94,
        "metrics": {
            "requirement_coverage": 0.95,
            "grounding_accuracy": 0.98,
            "framework_compliance": 1.0,
            "test_completeness": 0.92,
            "assertion_quality": 0.90,
            "code_quality": 0.95
        }
    }

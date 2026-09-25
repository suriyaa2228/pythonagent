"""
LangGraph Strongly-Typed Agent State
====================================
Defines AgentState TypedDict as specified in Section 7 of the Target Architecture.
"""

from typing import TypedDict, Optional, List, Dict, Any


class AgentState(TypedDict, total=False):
    request_id: str

    user_story: str
    acceptance_criteria: List[str]

    test_plan: Optional[Dict[str, Any]]

    retrieved_context: List[Dict[str, Any]]
    retrieved_symbols: List[Dict[str, Any]]
    retrieved_patterns: List[Dict[str, Any]]

    generated_dsl: Optional[Dict[str, Any]]
    generated_script: Optional[str]

    ast_valid: bool
    pom_valid: bool
    security_valid: bool
    grounding_valid: bool

    evaluation_score: Optional[float]
    evaluation_results: Optional[Dict[str, Any]]
    evaluation_feedback: Optional[List[str]]

    execution_status: Optional[str]
    execution_logs: Optional[str]

    failure_type: Optional[str]
    failure_evidence: Optional[Dict[str, Any]]

    generation_attempts: int
    healing_attempts: int

    final_decision: Optional[str]

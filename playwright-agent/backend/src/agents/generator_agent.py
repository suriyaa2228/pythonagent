"""
Playwright Generator Agent
===========================
Generates production-grade, AST-validated Python Playwright scripts aligned
with existing Page Object Models, custom pytest fixtures, and Extent Reporter calls.
"""

from typing import Any, Dict, List, Optional
from generation.orchestrator import GenerationOrchestrator


class PlaywrightGenerator:
    def __init__(self, orchestrator: GenerationOrchestrator):
        self.orchestrator = orchestrator

    def generate_script(
        self,
        user_story: str,
        acceptance_criteria: List[str],
        project: str = "playwright",
        environment: str = "stage"
    ) -> Dict[str, Any]:
        """
        Generates Python Playwright test script using RAG ingestion pipeline,
        structured prompting, and bounded self-correction AST quality gates.
        """
        result = self.orchestrator.generate_test_script(
            user_story=user_story,
            acceptance_criteria=acceptance_criteria,
            project=project,
            environment=environment
        )
        return result

    def generate_from_test_plan(
        self,
        test_plan: Dict[str, Any],
        project: str = "playwright",
        environment: str = "stage"
    ) -> Dict[str, Any]:
        """
        Generates Python Playwright test script directly from a Planner Agent output object.
        """
        tc = test_plan.get("testCases", [{}])[0]
        user_story = f"Plan {test_plan.get('testPlanId', 'PLAN')}: {tc.get('description', test_plan.get('useCaseSummary', ''))}"
        steps = [f"Step {s.get('stepId')}: {s.get('action')} on {s.get('target')} - {s.get('expectedResult', '')}" for s in tc.get("steps", [])]

        result = self.generate_script(
            user_story=user_story,
            acceptance_criteria=steps,
            project=project,
            environment=environment
        )

        result["testCaseNumber"] = tc.get("testCaseNumber", "TC001")
        result["testCaseName"] = tc.get("testCaseName", "GeneratedTest")
        return result

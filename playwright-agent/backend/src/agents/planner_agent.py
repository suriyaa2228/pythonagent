"""
Playwright Planner Agent
========================
Drafts structured, modular test plans and step specifications from user stories,
use cases, and acceptance criteria using the framework's core LLM interface.
"""

import json
from typing import Any, Dict, List, Optional
from generation.orchestrator import GenerationOrchestrator


PLANNER_SYSTEM_PROMPT = """You are the Playwright Planner Agent for the Momentec Python Playwright testing framework.
Your task is to decompose high-level user stories, use cases, and acceptance criteria into a structured, modular Test Plan aligned with existing Page Object Models (`HomePage`, `LoginPage`, `CustomSublimationPage`, `ConfiguratorPage`, `CartPage`, `ShippingBillingPage`, `ReviewSubmitPage`, `ThankYouPage`).

Output strictly valid JSON with the following schema:
{
  "testPlanId": "PLAN-023",
  "useCaseSummary": "Verify Sublimation Order placing flow with text and mascot",
  "testCases": [
    {
      "testCaseNumber": "TC023",
      "testCaseName": "SublimationOrderTextMascot",
      "description": "Detailed goal of the test case",
      "preconditions": [
        "Browser initialized with session storage state (tc023_state.json)",
        "User is logged in on Momentec stage environment"
      ],
      "steps": [
        {
          "stepId": 1,
          "action": "CLEAR_CART | NAVIGATE | VERIFY_TITLE | CLICK_CUSTOMIZE | ACCEPT_COOKIES | SELECT_DESIGN | NEXT_COLOR | SELECT_COLOR | NEXT_TEXT_LOGO | ADD_TEXT | ADD_ART | NEXT_ROSTER | ADD_ROSTER | NEXT_SUMMARY | ADD_TO_CART | FILL_CART_POPUP | CHECKOUT | SELECT_FEDEX_GROUND | REVIEW_SUBMIT | PLACE_ORDER",
          "target": "target element or page object method",
          "value": "optional parameter value (e.g., style_number '227232')",
          "expectedResult": "Expected verification or page transition"
        }
      ],
      "postconditions": ["Order placed and order number captured in Extent Report"]
    }
  ]
}
Do NOT wrap output in extra commentary. Output only the JSON object.
"""


class PlaywrightPlanner:
    def __init__(self, orchestrator: GenerationOrchestrator):
        self.orchestrator = orchestrator

    def draft_test_plan(
        self,
        use_case: str,
        acceptance_criteria: List[str],
        project: str = "playwright",
        environment: str = "stage"
    ) -> Dict[str, Any]:
        """
        Generates structured test plan specification from raw requirements.
        """
        ac_text = "\n".join([f"- {ac}" for ac in acceptance_criteria])
        user_prompt = f"Use Case:\n{use_case}\n\nAcceptance Criteria:\n{ac_text}\n\nTarget Environment: {environment}"

        messages = [
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        raw_res = self.orchestrator._call_llm(messages)
        parsed = self._parse_json(raw_res, use_case)
        return parsed

    def _parse_json(self, raw_res: str, fallback_title: str) -> Dict[str, Any]:
        data = None
        try:
            data = json.loads(raw_res)
        except Exception:
            import re
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_res)
            if match:
                try:
                    data = json.loads(match.group(1))
                except Exception:
                    pass

        if isinstance(data, dict):
            if "testCases" in data and isinstance(data["testCases"], list):
                return data
            # Transform template structure into standard Planner schema
            return {
                "testPlanId": f"PLAN-{data.get('testCaseId', '101')}",
                "useCaseSummary": data.get("description", fallback_title),
                "testCases": [
                    {
                        "testCaseNumber": data.get("testCaseId", "TC-101"),
                        "testCaseName": data.get("testName", "Default_Test_Case"),
                        "description": data.get("description", fallback_title),
                        "preconditions": ["Browser initialized with desktop viewport"],
                        "steps": [
                            {"stepId": idx + 1, "action": "STEP", "target": item.get("criterion", "Action"), "value": item.get("mappedStep", ""), "expectedResult": "Step completed"}
                            for idx, item in enumerate(data.get("acceptanceCriteriaMapping", []))
                        ] or [{"stepId": 1, "action": "NAVIGATE", "target": "Home Page", "value": "/", "expectedResult": "Page loaded"}],
                        "postconditions": ["Session closed"]
                    }
                ]
            }

        return {
            "testPlanId": "PLAN-FALLBACK",
            "useCaseSummary": fallback_title,
            "testCases": [
                {
                    "testCaseNumber": "TC-101",
                    "testCaseName": "Default_Test_Case",
                    "description": fallback_title,
                    "preconditions": ["Browser initialized"],
                    "steps": [
                        {"stepId": 1, "action": "NAVIGATE", "target": "Home Page", "value": "/", "expectedResult": "Page loads successfully"}
                    ],
                    "postconditions": []
                }
            ]
        }


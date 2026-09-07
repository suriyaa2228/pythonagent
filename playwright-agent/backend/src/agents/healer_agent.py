"""
Playwright Healer Agent
========================
Analyzes test execution failures, DOM dumps, and stack traces to automatically
repair broken locators and syntax errors in Python Playwright scripts.
"""

import json
import os
import re
from typing import Any, Dict, Optional
from generation.orchestrator import GenerationOrchestrator


HEALER_SYSTEM_PROMPT = """You are the Playwright Healer Agent for the Momentec Python Playwright testing framework.
Your task is to analyze a failed Python Playwright script along with execution stack traces and DOM dump excerpts, identify the root cause (such as broken locators, timeout errors, outdated element IDs, missing page object imports, or improper storage state reuse), and output a healed Python script.

MANDATORY HEALING RULES:
1. Preserve `@pytest.mark.usefixtures("auth_page_tcXXX")` class scoping and `auth_context_tcXXX` storage state reuse.
2. Maintain `Reporter.start_test_case(...)` and `Reporter.report_step(page, description, status)` calls.
3. Replace hardcoded `.first` locator queries with explicit parameters (e.g. `custom_sublimation_page.click_customize_on_product("227232")`).
4. Keep all existing Page Object Model method calls intact.

Output strictly valid JSON with the following schema:
{
  "isHealed": true,
  "healingSummary": "Updated click_customize_on_product argument to target product style '227232' and added resilient selector fallback.",
  "repairedLocators": [
    {
      "original": "locator('a:has-text(\"Customize\")').first",
      "repaired": "click_customize_on_product(\"227232\")",
      "reason": "Hardcoded .first locator was selecting the wrong product card on the PLP grid"
    }
  ],
  "pythonScript": "Complete healed Python Playwright script code here..."
}
Do NOT wrap output in extra commentary. Output only the JSON object.
"""


class PlaywrightHealer:
    def __init__(self, orchestrator: GenerationOrchestrator):
        self.orchestrator = orchestrator

    def heal_script(
        self,
        failed_script: str,
        error_message: str,
        dom_dump_path: Optional[str] = None,
        screenshot_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyzes failure context and returns a healed Python Playwright script.
        """
        dom_excerpt = ""
        if dom_dump_path and os.path.exists(dom_dump_path):
            try:
                with open(dom_dump_path, "r", encoding="utf-8", errors="ignore") as f:
                    dom_content = f.read()
                    # Limit DOM dump excerpt to 4000 characters to prevent context window overflow
                    dom_excerpt = dom_content[:4000]
            except Exception as e:
                dom_excerpt = f"Could not read DOM dump file: {e}"

        user_prompt = (
            f"FAILED SCRIPT:\n```python\n{failed_script}\n```\n\n"
            f"ERROR STACK TRACE / LOG:\n{error_message}\n\n"
            f"{'DOM DUMP EXCERPT:' if dom_excerpt else ''}\n{dom_excerpt}"
        )

        messages = [
            {"role": "system", "content": HEALER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        raw_res = self.orchestrator._call_llm(messages)
        parsed = self._parse_json(raw_res, failed_script)

        healed_code = parsed.get("pythonScript", failed_script)
        val_res = self.orchestrator.validator.validate_script(healed_code)
        parsed["validation"] = val_res.to_dict()

        return parsed

    def _parse_json(self, raw_res: str, original_script: str) -> Dict[str, Any]:
        try:
            return json.loads(raw_res)
        except Exception:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_res)
            if match:
                try:
                    return json.loads(match.group(1))
                except Exception:
                    pass

        return {
            "isHealed": False,
            "healingSummary": "Could not auto-heal script using structured JSON.",
            "repairedLocators": [],
            "pythonScript": original_script
        }

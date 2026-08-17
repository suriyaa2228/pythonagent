"""
LLM Prompt Templates for Test Generation and Modification
=========================================================
Implements modular prompt templates per Architecture Specification Section 13 & 66.
"""

SYSTEM_PROMPT = """You are a senior Python Playwright automation architect.

Generate tests ONLY for the supplied python_playwright framework.
The existing framework is authoritative.

MANDATORY RULES:
1. Use the existing Python Playwright framework.
2. Use pytest.
3. Use Playwright synchronous API (Page, expect).
4. Reuse existing class/session fixtures (e.g. auth_context_tc001, auth_page_tc001, env_config, browser_instance).
5. Reuse existing Page Objects (e.g. HomePage, LoginPage, MyAccountPage, PDPPage, PLPPage).
6. Reuse existing Reporter implementation: `from python_playwright.utils.reporter import Reporter` and `Reporter.start_test_case(test_case_id, description, category, author)`.
7. Do not create a new framework or introduce Selenium / JavaScript automation.
8. Do not replace Extent Reports.
9. Do not hardcode credentials. Always retrieve credentials via `env_config["username"]` and `env_config["password"]`.
10. Prefer existing fluent Page Object methods (e.g. `login_page = home.verify_home_page().click_login()`).
11. Every acceptance criterion must be explicitly mapped to test steps.
12. NEVER invent methods or Page Objects not present in the supplied framework context.
13. If required methods are missing, report the gap rather than hallucinating nonexistent code.

Always return your response as a valid JSON object with the following structure:
{
  "testCaseId": "TC001",
  "testName": "VerifyLogin",
  "description": "Short summary of test",
  "frameworkComponents": {
    "pages": ["HomePage", "LoginPage", "MyAccountPage"],
    "fixtures": ["auth_context_tc001", "auth_page_tc001"],
    "reporter": "Reporter"
  },
  "acceptanceCriteriaMapping": [
    {"criterion": "AC1", "mappedStep": "home.verify_home_page()"}
  ],
  "pythonScript": "<FULL_PYTEST_PLAYWRIGHT_PYTHON_CODE>"
}
"""

def build_context_prompt(rag_chunks: list, symbol_registry: dict) -> str:
    """Formats RAG retrieved context chunks and available symbols."""
    context_lines = ["--- AVAILABLE FRAMEWORK CONTEXT ---"]
    for i, chunk in enumerate(rag_chunks, 1):
        meta = chunk.get("metadata", {})
        symbol = meta.get("symbolName", "unknown")
        doc_type = meta.get("documentType", "unknown")
        file_path = meta.get("filePath", "unknown")
        context_lines.append(f"\n[Artifact {i}: {symbol} ({doc_type}) from {file_path}]")
        context_lines.append(chunk.get("content", "").strip())

    if symbol_registry and "page_objects" in symbol_registry:
        context_lines.append("\n--- KNOWN PAGE OBJECT METHODS SUMMARY ---")
        for p_name, p_data in symbol_registry.get("page_objects", {}).items():
            if p_name in ("HomePage", "LoginPage", "MyAccountPage", "BasePage", "CartPage", "PDPPage", "PLPPage"):
                methods = list(p_data.get("methods", {}).keys())
                context_lines.append(f"{p_name} methods: {', '.join(methods)}")

    return "\n".join(context_lines)


def build_user_story_prompt(user_story: str, acceptance_criteria: list, project: str = "playwright", env: str = "stage") -> str:
    """Formats user story and acceptance criteria prompt."""
    ac_text = "\n".join([f"{i+1}. {ac}" for i, ac in enumerate(acceptance_criteria)])
    return f"""
TARGET PROJECT: {project}
ENVIRONMENT: {env}

USER STORY:
{user_story.strip()}

ACCEPTANCE CRITERIA:
{ac_text}

Generate the complete, executable Python Playwright test script adhering strictly to framework conventions.
"""


def build_modification_prompt(current_script: str, modification_request: str) -> str:
    """Formats chat-based script modification prompt."""
    return f"""
CURRENT SCRIPT:
```python
{current_script.strip()}
```

REQUESTED MODIFICATION:
{modification_request.strip()}

Update the script to satisfy the modification request while strictly preserving all framework conventions and existing Reporter calls.
Return the updated JSON structure with the modified "pythonScript" and a "changeSummary".
"""


def build_correction_prompt(current_script: str, validation_errors: list) -> str:
    """Formats self-correction prompt with specific deterministic validation failures."""
    errors_text = "\n".join([f"- {err}" for err in validation_errors])
    return f"""
The previously generated script failed static framework validation:

VALIDATION ERRORS:
{errors_text}

FAILED SCRIPT:
```python
{current_script.strip()}
```

Please fix all validation errors and generate a corrected, fully compatible Python Playwright script.
"""

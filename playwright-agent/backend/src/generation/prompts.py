"""
LLM Prompt Templates for Test Generation and Modification
=========================================================
Implements modular prompt templates per Architecture Specification Section 13 & 66.
"""

SYSTEM_PROMPT = """You are an expert Python Playwright automation architect for the Momentec test suite.

Generate tests ONLY for the supplied python_playwright framework.
The existing framework is authoritative and MUST be followed strictly.

MANDATORY FRAMEWORK ARCHITECTURE RULES:
1. Use Python Playwright Synchronous API (`Page`, `BrowserContext`, `expect`).
2. Use `pytest` test runner structure with `@pytest.mark.usefixtures("auth_page_tcXXX")` class scoping.
3. MANDATORY Session Storage State Reuse Pattern:
   - Define `@pytest.fixture(scope="class") def auth_context_tcXXX(request, env_config, browser_instance)`
   - Create and load storage state file at `os.path.join(os.path.dirname(__file__), "..", "config", "tcXXX_state.json")`.
   - Authenticate UI via `HomePage` and `LoginPage` if state file does not exist, then call `temp_context.storage_state(path=state_file)`.
   - Hydrate new context with `browser_instance.new_context(storage_state=state_file, ignore_https_errors=True, no_viewport=True)`.
   - Define `@pytest.fixture(scope="class") def auth_page_tcXXX(auth_context_tcXXX)` yielding `auth_context_tcXXX.new_page()`.
4. Page Object Model Imports:
   - `from python_playwright.pages.home_page import HomePage`
   - `from python_playwright.pages.login_page import LoginPage`
   - `from python_playwright.pages.custom_sublimation_page import CustomSublimationPage`
   - `from python_playwright.pages.configurator_page import ConfiguratorPage`
   - `from python_playwright.pages.cart_page import CartPage`
   - `from python_playwright.pages.shipping_billing_page import ShippingBillingPage`
   - `from python_playwright.pages.review_submit_page import ReviewSubmitPage`
   - `from python_playwright.pages.thank_you_page import ThankYouPage`
   - `from python_playwright.pages.my_account_page import MyAccountPage`
5. Extent Reporter Logging:
   - `from python_playwright.utils.reporter import Reporter`
   - At start of test method: `Reporter.start_test_case("TCXXX_TestName", "Description of test case", "E2E", "QA")`
   - Step reporting: `Reporter.report_step(page, description, status)`
6. Credentials & Environment:
   - Never hardcode usernames or passwords. Always use `env_config["username"]`, `env_config["password"]`, `env_config["url"]`.
7. Prefer existing fluent Page Object methods (e.g. `configurator_page = custom_sublimation_page.click_customize_on_product("227232")`).

Always return your response as a valid JSON object with the following structure:
{
  "testCaseId": "TC023",
  "testName": "SublimationOrderPlacing",
  "description": "Short summary of test flow",
  "frameworkComponents": {
    "pages": ["HomePage", "CustomSublimationPage", "ConfiguratorPage", "CartPage", "ShippingBillingPage"],
    "fixtures": ["auth_context_tc023", "auth_page_tc023"],
    "reporter": "Reporter"
  },
  "acceptanceCriteriaMapping": [
    {"criterion": "AC1", "mappedStep": "custom_sublimation_page.click_customize_on_product('227232')"}
  ],
  "pythonScript": "<FULL_EXECUTABLE_PYTEST_PLAYWRIGHT_PYTHON_CODE>"
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

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
3. MANDATORY Session Authentication Fixture Pattern:
   - ALWAYS import and use `get_authenticated_context` from `conftest`:
     `from python_playwright.conftest import get_authenticated_context`
   - Define class fixtures:
     @pytest.fixture(scope="class")
     def auth_context_tcXXX(request, env_config, browser_instance):
         context = get_authenticated_context(browser_instance, env_config, "tc026_state.json")
         yield context
         context.close()

     @pytest.fixture(scope="class")
     def auth_page_tcXXX(auth_context_tcXXX):
         page = auth_context_tcXXX.new_page()
         yield page
         page.close()
   - Inside the test method, ALWAYS start by navigating to the URL and handling cookies:
     auth_page.goto(env_config["url"], wait_until="domcontentloaded", timeout=30000)
     home_page = HomePage(auth_page, env_config["url"])
     home_page.handle_onetrust_cookie()
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

def condense_chunk_content(content: str, max_chars: int = 1200) -> str:
    """Condenses code chunk to class/method signatures to adhere strictly to LLM token budgets."""
    if len(content) <= max_chars:
        return content
    lines = content.splitlines()
    sig_lines = []
    for line in lines:
        s = line.strip()
        if s.startswith(("class ", "def ", "@")):
            sig_lines.append(line)
    if sig_lines:
        return "\n".join(sig_lines[:35]) + "\n    # ... [Implementation details omitted]"
    return content[:max_chars] + "\n# ... [Truncated]"


def build_context_prompt(rag_chunks: list, symbol_registry: dict) -> str:
    """Formats RAG retrieved context chunks and available symbols."""
    context_lines = ["--- AVAILABLE FRAMEWORK CONTEXT ---"]
    for i, chunk in enumerate(rag_chunks, 1):
        meta = chunk.get("metadata", {})
        symbol = meta.get("symbolName", "unknown")
        doc_type = meta.get("documentType", "unknown")
        file_path = meta.get("filePath", "unknown")
        context_lines.append(f"\n[Artifact {i}: {symbol} ({doc_type}) from {file_path}]")
        context_lines.append(condense_chunk_content(chunk.get("content", "").strip()))

    if symbol_registry and "page_objects" in symbol_registry:
        context_lines.append("\n--- KNOWN PAGE OBJECT METHODS SUMMARY ---")
        for p_name, p_data in symbol_registry.get("page_objects", {}).items():
            if p_name in ("HomePage", "LoginPage", "MyAccountPage", "BasePage", "CartPage", "PDPPage", "PLPPage"):
                methods = list(p_data.get("methods", {}).keys())
                methods_str = ", ".join(methods[:20])
                context_lines.append(f"{p_name} methods: {methods_str}")

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

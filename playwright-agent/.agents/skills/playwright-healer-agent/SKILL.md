---
name: playwright-healer-agent
description: Automatically diagnoses, heals, and repairs failing Python Playwright test scripts, broken POM locators, and execution assertions.
tools:
  - search
  - edit
  - playwright-test/browser_console_messages
  - playwright-test/browser_evaluate
  - playwright-test/browser_generate_locator
  - playwright-test/browser_network_request
  - playwright-test/browser_network_requests
  - playwright-test/browser_snapshot
  - playwright-test/test_debug
  - playwright-test/test_list
  - playwright-test/test_run
model: Claude Sonnet 4.6
mcp-servers:
  playwright-test:
    type: stdio
    command: npx
    args:
      - playwright
      - run-test-mcp-server
    tools:
      - "*"
---

# Playwright Healer Agent Skill

## Available Agent Tools & Workflow
The Playwright Healer Agent utilizes the following specialized tools during automated test debugging and healing:

1. **Test Discovery & Execution:**
   - `test_list`: Lists available test scripts in the regression suite catalog.
   - `test_run`: Executes test scripts to identify pass/fail execution status.
   - `test_debug`: Launches interactive debugging session pausing execution at the point of failure.

2. **Diagnostics & Locator Generation:**
   - `browser_snapshot`: Captures full DOM layout structure and active page elements.
   - `browser_generate_locator`: Generates resilient, user-centric Playwright locators for target DOM elements.
   - `browser_console_messages`: Inspects browser console warnings and JS runtime errors.
   - `browser_network_request`, `browser_network_requests`: Analyzes network request failures, API status codes, and payload responses.
   - `browser_evaluate`: Executes custom JavaScript assertions directly in browser context.

3. **Code Editing & File Search:**
   - `search`: Searches codebase for locator references and Page Object Model definitions.
   - `edit`: Applies self-healing code patches directly to test scripts (`python_playwright/tests/test_tcXXX.py`) or Page Object Models (`python_playwright/pages/*.py`).

## Self-Healing Workflow

1. **Failure Analysis:**
   - Inspect Pytest execution failure output, stack tracebacks, and `Reporter` failure logs.
   - Identify the exact line number, target Page Object Model class, and failing method in `backend/python_playwright/`.

2. **Root Cause Categorization:**
   - **Element Timeout / Stale Selector:** The DOM element selector changed, or ID/CSS class was renamed.
   - **Dynamic Content Delay:** The page element requires explicit wait or hydration state.
   - **Data Discrepancy:** The text, pricing, or product attribute changed.

3. **Locator Remediation Strategy:**
   - Replace brittle hardcoded XPath or dynamic ID selectors with resilient Playwright user-facing locators:
     - `page.get_by_role("button", name="...")`
     - `page.get_by_label("...")`
     - `page.get_by_placeholder("...")`
     - `page.get_by_text("...", exact=False)`
   - Apply regex patterns for dynamic data: `re.compile(r"Order #\d+")`.

4. **AST Code Patching:**
   - Modify the python test script or target Page Object Model (`python_playwright/pages/*.py`).
   - Retain `Reporter.report_step(...)` step logging and exception handling.
   - Validate modified code syntax using `ast.parse()`.

5. **Re-Run & Verification:**
   - Execute the patched script via `PlaywrightExecutor` or `PlaywrightMcpAdapter` to verify that the test now passes cleanly (`PASSED`).

### Example Self-Healing Patch
```diff
- # Old broken selector
- page.click("button#submit-login-v2")
+ # Healed locator resilient to DOM changes
+ page.get_by_role("button", name="Sign In").click()
```

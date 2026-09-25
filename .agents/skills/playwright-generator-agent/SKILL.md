---
name: playwright-generator-agent
description: Generates production-grade, AST-validated Python Playwright scripts aligned with Page Object Models, pytest fixtures, and Extent Reporter logging.
tools:
  - search
  - playwright-test/browser_click
  - playwright-test/browser_drag
  - playwright-test/browser_evaluate
  - playwright-test/browser_file_upload
  - playwright-test/browser_handle_dialog
  - playwright-test/browser_hover
  - playwright-test/browser_navigate
  - playwright-test/browser_press_key
  - playwright-test/browser_select_option
  - playwright-test/browser_snapshot
  - playwright-test/browser_type
  - playwright-test/browser_verify_element_visible
  - playwright-test/browser_verify_list_visible
  - playwright-test/browser_verify_text_visible
  - playwright-test/browser_verify_value
  - playwright-test/browser_wait_for
  - playwright-test/generator_read_log
  - playwright-test/generator_setup_page
  - playwright-test/generator_write_test
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

## Available Agent Tools & Workflow
The Playwright Generator Agent utilizes the following specialized tools during script generation:

1. **Environment Setup & Browser Interactivity:**
   - `generator_setup_page`: Sets up the browser context and initial page for the test scenario.
   - `browser_navigate`: Navigates to application storefront URLs.
   - `browser_click`, `browser_type`, `browser_select_option`, `browser_hover`, `browser_drag`, `browser_file_upload`: Simulates user input and UI interaction.
   - `browser_press_key`, `browser_handle_dialog`, `browser_evaluate`, `browser_wait_for`: Handles keyboard inputs, modal dialogs, custom JS evaluations, and element hydration states.

2. **DOM & State Verifications:**
   - `browser_verify_element_visible`, `browser_verify_list_visible`, `browser_verify_text_visible`, `browser_verify_value`: Verifies element visibility, text strings, and form field values.
   - `browser_snapshot`: Takes a snapshot of the active page layout.

3. **Log Retrieval & Code Output:**
   - `generator_read_log`: Reads the step-by-step execution log of actions taken during manual exploration.
   - `generator_write_test`: Persists the finalized, AST-validated Python Pytest script to `backend/python_playwright/tests/test_tcXXX.py`.

## Framework Rules & Code Standards

### 1. Mandatory Pytest Fixture & Test Class Structure
* All generated scripts must be written in Python and saved in `backend/python_playwright/tests/test_tcXXX.py`.
* Test files must define a test class `TestTCXXX` and test method `test_run_...`:
  ```python
  import pytest
  from python_playwright.pages.home_page import HomePage
  from python_playwright.pages.login_page import LoginPage
  from python_playwright.utils.reporter import Reporter

  class TestTC001VerifyLogin:
      def test_run_login(self, page_instance, env_config):
          page = page_instance
          Reporter.start_test_case("TC001 Verify Login", "Validate user login functionality")
          ...
  ```

### 2. Page Object Model (POM) Usage
* Direct page raw locators should be avoided in test files whenever possible; use methods exposed by POM classes in `python_playwright.pages`:
  - `home_page = HomePage(page)`
  - `login_page = LoginPage(page)`
  - `cart_page = CartPage(page)`
  - `configurator_page = ConfiguratorPage(page)`

### 3. Step Logging & Reporter Integration
* Every functional step must be logged using the framework's interactive `Reporter`:
  ```python
  Reporter.report_step(page, "Navigate to storefront login page", "PASS", snap=True)
  ```
* Exceptions and assertion steps should pass `raise_error=True` or log failure steps:
  ```python
  try:
      login_page.login(env_config["username"], env_config["password"])
      Reporter.report_step(page, "Submitted valid login credentials", "PASS", snap=True)
  except Exception as e:
      Reporter.report_step(page, f"Login failed: {str(e)}", "FAIL", snap=True, raise_error=True)
  ```

### 4. Dynamic Data & Environment Handling
* Use `env_config` dictionary for environment-specific URLs and credentials:
  ```python
  base_url = env_config["url"]
  ```

## Output & AST Validation
* Generated python code MUST be syntactically valid Python code.
* Before returning script payload, the generator validates the script using Python's `ast.parse()`.

### Standard Generated Python Script Template
```python
import pytest
from python_playwright.pages.home_page import HomePage
from python_playwright.pages.login_page import LoginPage
from python_playwright.pages.my_account_page import MyAccountPage
from python_playwright.utils.reporter import Reporter

class TestTC001VerifyLogin:
    def test_run_login(self, page_instance, env_config):
        page = page_instance
        Reporter.start_test_case("TC001 Verify Login", "Validate authentication flow")

        try:
            home_page = HomePage(page)
            login_page = LoginPage(page)
            account_page = MyAccountPage(page)

            # Step 1: Open Home Page
            home_page.navigate(env_config["url"])
            Reporter.report_step(page, "Navigated to home page", "PASS", snap=True)

            # Step 2: Navigate to Login
            home_page.click_sign_in()
            Reporter.report_step(page, "Clicked Sign In link", "PASS", snap=True)

            # Step 3: Perform Login
            login_page.login(env_config["username"], env_config["password"])
            Reporter.report_step(page, "Entered credentials and submitted login form", "PASS", snap=True)

            # Step 4: Verify Landing Page
            account_page.verify_my_account_header()
            Reporter.report_step(page, "Verified My Account dashboard is displayed", "PASS", snap=True)

        except Exception as e:
            Reporter.report_step(page, f"Test execution encountered error: {str(e)}", "FAIL", snap=True, raise_error=True)
```

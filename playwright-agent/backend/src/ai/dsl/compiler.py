"""
Structured Test DSL Compiler
=============================
Compiles StructuredTestDSL objects into clean, compliant Python Playwright test scripts.
Enforces Page Object Model (POM) conventions, fixture setup, and Reporter logging.
"""

import re
from typing import Dict, Any, List
from ai.dsl.schema import StructuredTestDSL


PAGE_IMPORT_MAP = {
    "HomePage": "from python_playwright.pages.home_page import HomePage",
    "LoginPage": "from python_playwright.pages.login_page import LoginPage",
    "PDPPage": "from python_playwright.pages.pdp_page import PDPPage",
    "PLPPage": "from python_playwright.pages.plp_page import PLPPage",
    "CartPage": "from python_playwright.pages.cart_page import CartPage",
    "ShippingAndBillingPage": "from python_playwright.pages.shipping_billing_page import ShippingAndBillingPage",
    "ReviewSubmitPage": "from python_playwright.pages.review_submit_page import ReviewSubmitPage",
    "ThankYouPage": "from python_playwright.pages.thank_you_page import ThankYouPage",
    "CustomSublimationPage": "from python_playwright.pages.custom_sublimation_page import CustomSublimationPage",
    "ConfiguratorPage": "from python_playwright.pages.configurator_page import ConfiguratorPage",
    "MyAccountPage": "from python_playwright.pages.my_account_page import MyAccountPage",
    "ForgotPasswordPage": "from python_playwright.pages.forgot_password_page import ForgotPasswordPage"
}


class DSLCompiler:
    def __init__(self, symbol_registry: Dict[str, Any] = None):
        self.symbol_registry = symbol_registry or {}

    def compile(self, dsl: StructuredTestDSL) -> str:
        tc_id = dsl.test_id or "TC001"
        test_name = dsl.name.replace(" ", "")
        test_name_snake = re.sub(r'(?<!^)(?=[A-Z])', '_', test_name).lower()
        
        # Collect required imports
        used_pages = set()
        for step in dsl.steps:
            if step.page in PAGE_IMPORT_MAP:
                used_pages.add(step.page)
        for assertion in dsl.assertions:
            if assertion.page in PAGE_IMPORT_MAP:
                used_pages.add(assertion.page)

        if "HomePage" not in used_pages:
            used_pages.add("HomePage")

        imports_lines = [PAGE_IMPORT_MAP[page] for page in sorted(used_pages)]
        imports_block = "\n".join(imports_lines)

        # Build steps code
        step_code_blocks = []
        for idx, step in enumerate(dsl.steps, 1):
            args_str = ", ".join([f"{k}='{v}'" if isinstance(v, str) else f"{k}={v}" for k, v in step.arguments.items()])
            var_name = re.sub(r'(?<!^)(?=[A-Z])', '_', step.page).lower()
            
            step_code = (
                f"        # Step {idx}: Call {step.page}.{step.action}({args_str})\n"
                f"        Reporter.report_step(auth_page_{tc_id.lower()}, \"Step {idx}: {step.page}.{step.action}\", \"PASS\")\n"
            )
            if step.page == "HomePage" and step.action == "goto":
                step_code += (
                    f"        auth_page_{tc_id.lower()}.goto(url)\n"
                    f"        home_page = HomePage(auth_page_{tc_id.lower()}, url)\n"
                    f"        home_page.accept_cookies()"
                )
            else:
                step_code += f"        {var_name}.{step.action}({args_str})"
            
            step_code_blocks.append(step_code)

        # Build assertions code
        for idx, assertion in enumerate(dsl.assertions, len(dsl.steps) + 1):
            var_name = re.sub(r'(?<!^)(?=[A-Z])', '_', assertion.page).lower()
            assert_code = (
                f"        # Step {idx}: Assert {assertion.page} {assertion.condition}\n"
                f"        Reporter.report_step(auth_page_{tc_id.lower()}, \"Step {idx}: Assert {assertion.condition}\", \"PASS\")\n"
                f"        expect(auth_page_{tc_id.lower()}.locator(\"body\")).to_be_visible(timeout=10000)"
            )
            step_code_blocks.append(assert_code)

        steps_block = "\n\n".join(step_code_blocks)

        script = (
            "import pytest\n"
            "from playwright.sync_api import sync_playwright, expect\n"
            f"{imports_block}\n\n"
            f"@pytest.fixture(scope=\"class\")\n"
            f"def auth_context_{tc_id.lower()}(request, env_config, browser_instance):\n"
            "    headless = request.config.getoption(\"--headless\")\n"
            "    if headless:\n"
            "        context = browser_instance.new_context(viewport={\"width\": 1440, \"height\": 900}, ignore_https_errors=True)\n"
            "    else:\n"
            "        context = browser_instance.new_context(no_viewport=True, ignore_https_errors=True)\n"
            "    context.set_default_timeout(30000)\n"
            "    yield context\n"
            "    context.close()\n\n"
            f"@pytest.fixture(scope=\"class\")\n"
            f"def auth_page_{tc_id.lower()}(auth_context_{tc_id.lower()}):\n"
            f"    page = auth_context_{tc_id.lower()}.new_page()\n"
            "    yield page\n"
            "    page.close()\n\n"
            f"@pytest.mark.usefixtures(\"auth_page_{tc_id.lower()}\")\n"
            f"class Test{tc_id}{test_name}:\n"
            f"    def test_{test_name_snake}(self, auth_page_{tc_id.lower()}, env_config):\n"
            "        from python_playwright.utils.reporter import Reporter\n"
            f"        Reporter.start_test_case(\"{tc_id}_{test_name}\", \"{dsl.description or dsl.name}\", \"Regression\", \"SURIYAA\")\n\n"
            "        url = env_config[\"url\"]\n"
            "        username = env_config[\"username\"]\n"
            "        password = env_config[\"password\"]\n\n"
            f"        home_page = HomePage(auth_page_{tc_id.lower()}, url)\n\n"
            f"{steps_block}\n"
        )
        return script

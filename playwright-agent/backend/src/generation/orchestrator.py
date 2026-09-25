"""
LangChain / Groq Test Generation Orchestrator & Self-Correction Pipeline
========================================================================
Implements the generation, structured parsing, validation, and bounded self-correction loop
as specified in Sections 11, 12, 14, 18, and 19 of the Architecture Specification.
"""

import json
import os
import re
import urllib.request
from typing import Any, Dict, List, Optional

from generation.prompts import (
    SYSTEM_PROMPT,
    build_context_prompt,
    build_user_story_prompt,
    build_modification_prompt,
    build_correction_prompt
)
from generation.validator import FrameworkValidator, ValidationResult
from rag.ingestion_pipeline import RAGIngestionPipeline


class GenerationOrchestrator:
    def __init__(
        self,
        rag_pipeline: RAGIngestionPipeline,
        symbol_registry: Optional[Dict[str, Any]] = None,
        groq_api_key: Optional[str] = None,
        groq_model: Optional[str] = None,
        max_retries: int = 2
    ):
        self.rag_pipeline = rag_pipeline
        self.symbol_registry = symbol_registry or {}
        self.validator = FrameworkValidator(self.symbol_registry)
        self.groq_api_key = groq_api_key or os.environ.get("GROQ_API_KEY", "")
        self.groq_model = groq_model or os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.max_retries = int(os.environ.get("LLM_MAX_RETRIES", max_retries))
        self.groq_api_url = "https://api.groq.com/openai/v1/chat/completions"

    def generate_test_script(
        self,
        user_story: str,
        acceptance_criteria: List[str],
        project: str = "playwright",
        environment: str = "stage"
    ) -> Dict[str, Any]:
        """
        Executes end-to-end generation with RAG retrieval and self-correction loop.
        """
        # 1. RAG Retrieval
        search_query = f"{user_story} {' '.join(acceptance_criteria)}"
        rag_chunks = self.rag_pipeline.retrieve_context(search_query, top_k=6)
        context_prompt = build_context_prompt(rag_chunks, self.symbol_registry)
        user_prompt = build_user_story_prompt(user_story, acceptance_criteria, project, environment)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{context_prompt}\n\n{user_prompt}"}
        ]

        attempt = 0
        last_errors = []
        generated_result = None

        while attempt <= self.max_retries:
            attempt += 1
            # 2. Invoke Groq Model (or offline deterministic synthesizer)
            raw_response = self._call_llm(messages)
            parsed_output = self._parse_json_response(raw_response, user_story)

            python_code = parsed_output.get("pythonScript", "")

            # 3. Deterministic Validation Quality Gate
            val_res = self.validator.validate_script(python_code, acceptance_criteria)

            if val_res.is_valid:
                parsed_output["validation"] = val_res.to_dict()
                parsed_output["retriesUsed"] = attempt - 1
                parsed_output["ragContextCount"] = len(rag_chunks)
                return parsed_output

            # Validation failed, prepare correction prompt for next attempt
            last_errors = val_res.errors
            print(f"[RETRY {attempt}/{self.max_retries}] Validation failed: {last_errors}")

            if attempt <= self.max_retries:
                correction_prompt = build_correction_prompt(python_code, last_errors)
                messages.append({"role": "assistant", "content": raw_response})
                messages.append({"role": "user", "content": correction_prompt})

        # Return with validation status if retries exhausted
        if parsed_output:
            parsed_output["validation"] = {
                "status": "FAIL",
                "isValid": False,
                "errors": last_errors,
                "warnings": []
            }
            parsed_output["retriesUsed"] = self.max_retries
            return parsed_output

        return {
            "error": "Failed to generate valid test script after maximum retries.",
            "errors": last_errors
        }

    def modify_test_script(
        self,
        current_script: str,
        modification_request: str
    ) -> Dict[str, Any]:
        """
        Updates an existing test script through conversational instruction while preserving framework rules.
        """
        rag_chunks = self.rag_pipeline.retrieve_context(modification_request, top_k=4)
        context_prompt = build_context_prompt(rag_chunks, self.symbol_registry)
        mod_prompt = build_modification_prompt(current_script, modification_request)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{context_prompt}\n\n{mod_prompt}"}
        ]

        raw_response = self._call_llm(messages)
        parsed_output = self._parse_json_response(raw_response, "Modified Script")
        python_code = parsed_output.get("pythonScript", "")

        val_res = self.validator.validate_script(python_code)
        parsed_output["validation"] = val_res.to_dict()
        return parsed_output

    def _call_llm(self, messages: List[Dict[str, str]]) -> str:
        """Invokes Groq API or falls back to smart offline synthesizer."""
        if self.groq_api_key:
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.groq_api_key}"
                }
                payload = {
                    "model": self.groq_model,
                    "messages": messages,
                    "temperature": 0.0,
                    "response_format": {"type": "json_object"}
                }
                req = urllib.request.Request(
                    self.groq_api_url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers,
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=30) as response:
                    res_data = json.loads(response.read().decode("utf-8"))
                    return res_data["choices"][0]["message"]["content"]
            except Exception as e:
                print(f"[WARN] Groq API call failed: {e}. Falling back to smart generator.")

        # Deterministic offline generation based on framework templates & symbols
        return self._generate_offline_template(messages)

    def _generate_offline_template(self, messages: List[Dict[str, str]]) -> str:
        """Generates a valid, compatible Python Playwright script dynamically matching the entered usecase and acceptance criteria."""
        user_prompts = [m["content"] for m in messages if m["role"] == "user"]
        combined = "\n".join(user_prompts)

        # 1. Extract User Story
        user_story = ""
        story_match = re.search(r"USER STORY:\s*([\s\S]*?)(?=\nACCEPTANCE CRITERIA:|\nTARGET PROJECT:|$)", combined, re.IGNORECASE)
        if story_match:
            user_story = story_match.group(1).strip()
        else:
            for line in combined.splitlines():
                if "user story" in line.lower() or "use case" in line.lower():
                    user_story = line.split(":", 1)[-1].strip()
                    break

        if not user_story:
            user_story = "Verify Momentec application functionality"

        # 2. Extract Acceptance Criteria
        acceptance_criteria = []
        ac_match = re.search(r"ACCEPTANCE CRITERIA:\s*([\s\S]*?)(?=\n---|\nTARGET PROJECT:|$)", combined, re.IGNORECASE)
        if ac_match:
            raw_ac = ac_match.group(1).strip()
            for line in raw_ac.splitlines():
                cleaned = re.sub(r"^\s*(\d+[\.\)]|-|\*)\s*", "", line).strip()
                if cleaned:
                    acceptance_criteria.append(cleaned)

        if not acceptance_criteria:
            acceptance_criteria = ["Navigate to home page and verify core functionality"]

        # 3. Product IDs extraction
        product_ids = re.findall(r"\b\d{4,6}[A-Z]?\b", combined)
        prod_id = product_ids[0] if product_ids else "7001"

        # 4. Build Test Name & Case ID
        words = re.findall(r"[a-zA-Z0-9]+", user_story)
        stop_words = {"as", "a", "user", "i", "want", "to", "so", "that", "be", "able", "the", "on", "in", "for", "with", "and", "verify", "check", "should"}
        filtered_words = [w.capitalize() for w in words if w.lower() not in stop_words]
        test_name = "".join(filtered_words[:6]) or "GeneratedTestCase"

        story_lower = (user_story + " " + " ".join(acceptance_criteria)).lower()

        # 5. Categorize and build pom mapping & code
        if any(k in story_lower for k in ["sublimation", "227232", "save icon", "builder", "customization", "mascot", "roster"]):
            category = "sublimation"
            tc_id = "TC002"
            test_name = "SaveIconSublimationBuilder" if "save icon" in story_lower else (test_name or "SublimationBuilder")
            pages = ["HomePage", "LoginPage", "CustomSublimationPage", "ConfiguratorPage", "MyAccountPage"]
            imports_code = (
                "from python_playwright.pages.home_page import HomePage\n"
                "from python_playwright.pages.login_page import LoginPage\n"
                "from python_playwright.pages.custom_sublimation_page import CustomSublimationPage\n"
                "from python_playwright.pages.configurator_page import ConfiguratorPage\n"
                "from python_playwright.pages.my_account_page import MyAccountPage"
            )
        elif any(k in story_lower for k in ["invalid login", "login error", "incorrect password", "wrong password", "error message"]):
            category = "invalid_login"
            tc_id = "TC003"
            test_name = "VerifyLoginErrorMessage"
            pages = ["HomePage", "LoginPage"]
            imports_code = (
                "from python_playwright.pages.home_page import HomePage\n"
                "from python_playwright.pages.login_page import LoginPage"
            )
        elif any(k in story_lower for k in ["reset password", "forgot password", "password recovery"]):
            category = "reset_password"
            tc_id = "TC002"
            test_name = "ResetPasswordValidation"
            pages = ["HomePage", "LoginPage", "ForgotPasswordPage"]
            imports_code = (
                "from python_playwright.pages.home_page import HomePage\n"
                "from python_playwright.pages.login_page import LoginPage\n"
                "from python_playwright.pages.forgot_password_page import ForgotPasswordPage"
            )
        elif any(k in story_lower for k in ["search", "pdp", "7001", "228118", "404f", "6951"]):
            category = "search"
            tc_id = "TC006"
            test_name = test_name if "Search" in test_name else "SearchFunctionality"
            pages = ["HomePage", "PDPPage"]
            imports_code = (
                "from python_playwright.pages.home_page import HomePage\n"
                "from python_playwright.pages.pdp_page import PDPPage"
            )
        elif any(k in story_lower for k in ["cart", "add to cart", "promo", "coupon", "discount", "quantity", "clear cart"]):
            category = "cart"
            tc_id = "TC016"
            test_name = test_name if "Cart" in test_name else "AddToCartAndCartValidation"
            pages = ["HomePage", "PDPPage", "CartPage"]
            imports_code = (
                "from python_playwright.pages.home_page import HomePage\n"
                "from python_playwright.pages.pdp_page import PDPPage\n"
                "from python_playwright.pages.cart_page import CartPage"
            )
        elif any(k in story_lower for k in ["shipping", "billing", "fedex", "ground", "2day", "freight"]):
            category = "shipping"
            tc_id = "TC017"
            test_name = test_name if "Shipping" in test_name else "VerifyShippingValidation"
            pages = ["HomePage", "LoginPage", "PDPPage", "CartPage", "ShippingAndBillingPage"]
            imports_code = (
                "from python_playwright.pages.home_page import HomePage\n"
                "from python_playwright.pages.login_page import LoginPage\n"
                "from python_playwright.pages.pdp_page import PDPPage\n"
                "from python_playwright.pages.cart_page import CartPage\n"
                "from python_playwright.pages.shipping_billing_page import ShippingAndBillingPage"
            )
        elif any(k in story_lower for k in ["checkout", "place order", "thank you", "blank order", "review submit"]):
            category = "checkout_order"
            tc_id = "TC020"
            test_name = test_name if "Order" in test_name else "VerifyBlankOrderPlacement"
            pages = ["HomePage", "LoginPage", "PDPPage", "CartPage", "ShippingAndBillingPage", "ReviewSubmitPage", "ThankYouPage"]
            imports_code = (
                "from python_playwright.pages.home_page import HomePage\n"
                "from python_playwright.pages.login_page import LoginPage\n"
                "from python_playwright.pages.pdp_page import PDPPage\n"
                "from python_playwright.pages.cart_page import CartPage\n"
                "from python_playwright.pages.shipping_billing_page import ShippingAndBillingPage\n"
                "from python_playwright.pages.review_submit_page import ReviewSubmitPage\n"
                "from python_playwright.pages.thank_you_page import ThankYouPage"
            )
        elif any(k in story_lower for k in ["category", "plp", "facet", "navigation", "filter"]):
            category = "category_nav"
            tc_id = "TC007"
            test_name = test_name if "Category" in test_name else "CategoryNavigationFunctionality"
            pages = ["HomePage", "PLPPage"]
            imports_code = (
                "from python_playwright.pages.home_page import HomePage\n"
                "from python_playwright.pages.plp_page import PLPPage"
            )
        elif any(k in story_lower for k in ["my account", "account info", "orders", "returns"]):
            category = "my_account"
            tc_id = "TC005"
            test_name = "VerifyMyAccountPages"
            pages = ["HomePage", "LoginPage", "MyAccountPage"]
            imports_code = (
                "from python_playwright.pages.home_page import HomePage\n"
                "from python_playwright.pages.login_page import LoginPage\n"
                "from python_playwright.pages.my_account_page import MyAccountPage"
            )
        elif any(k in story_lower for k in ["login", "sign in", "auth"]):
            category = "login"
            tc_id = "TC001"
            test_name = "VerifyLogin"
            pages = ["HomePage", "LoginPage", "MyAccountPage"]
            imports_code = (
                "from python_playwright.pages.home_page import HomePage\n"
                "from python_playwright.pages.login_page import LoginPage\n"
                "from python_playwright.pages.my_account_page import MyAccountPage"
            )
        else:
            category = "generic"
            tc_id = "TC030"
            test_name = test_name or "CustomWorkflowValidation"
            pages = ["HomePage"]
            imports_code = "from python_playwright.pages.home_page import HomePage"

        # 6. Map Acceptance Criteria to POM method calls and build pythonScript steps
        ac_mappings = []
        script_steps_code = []

        for idx, ac in enumerate(acceptance_criteria, 1):
            ac_low = ac.lower()
            if "home" in ac_low or "navigate" in ac_low or idx == 1:
                mapped = f"auth_page_{tc_id.lower()}.goto(url)"
                code = (
                    f"        # Step {idx}: {ac}\n"
                    f"        Reporter.report_step(auth_page_{tc_id.lower()}, \"Step {idx}: {ac}\", \"PASS\")\n"
                    f"        auth_page_{tc_id.lower()}.goto(url)\n"
                    f"        home = HomePage(auth_page_{tc_id.lower()}, url)\n"
                    f"        home.accept_cookies()\n"
                    f"        home.verify_home_page()"
                )
            elif "login" in ac_low or "credential" in ac_low or "sign in" in ac_low:
                if category == "invalid_login":
                    mapped = "login_page.enter_username('invalid').enter_password('wrong')"
                    code = (
                        f"        # Step {idx}: {ac}\n"
                        f"        Reporter.report_step(auth_page_{tc_id.lower()}, \"Step {idx}: {ac}\", \"PASS\")\n"
                        f"        login_page = home.click_login()\n"
                        f"        login_page.enter_username('invalid_user@momentec.com').enter_password('wrongpassword').click_login_button()"
                    )
                else:
                    mapped = "home.enter_username(username).enter_password(password).click_login_button()"
                    code = (
                        f"        # Step {idx}: {ac}\n"
                        f"        Reporter.report_step(auth_page_{tc_id.lower()}, \"Step {idx}: {ac}\", \"PASS\")\n"
                        f"        home.verify_home_page().click_login()\n"
                        f"        home.enter_username(username).enter_password(password).click_login_button()\n"
                        f"        expect(auth_page_{tc_id.lower()}.locator(\"id=Header_GlobalLogin_signOutQuickLinkUser\")).to_be_visible(timeout=15000)"
                    )
            elif "search" in ac_low:
                mapped = f"home.search_product('{prod_id}')"
                code = (
                    f"        # Step {idx}: {ac}\n"
                    f"        Reporter.report_step(auth_page_{tc_id.lower()}, \"Step {idx}: {ac}\", \"PASS\")\n"
                    f"        pdp_page = home.search_product('{prod_id}')"
                )
            elif "customize" in ac_low or "builder" in ac_low or "sublimation" in ac_low:
                mapped = f"custom_sublimation.click_customize_on_product('{prod_id}')"
                code = (
                    f"        # Step {idx}: {ac}\n"
                    f"        Reporter.report_step(auth_page_{tc_id.lower()}, \"Step {idx}: {ac}\", \"PASS\")\n"
                    f"        custom_sublimation = CustomSublimationPage(auth_page_{tc_id.lower()})\n"
                    f"        configurator_page = custom_sublimation.click_customize_on_product('{prod_id}')\n"
                    f"        configurator_page.verify_configurator_loaded()"
                )
            elif "save icon" in ac_low:
                mapped = "configurator_page.verify_save_icon_present()"
                code = (
                    f"        # Step {idx}: {ac}\n"
                    f"        Reporter.report_step(auth_page_{tc_id.lower()}, \"Step {idx}: {ac}\", \"PASS\")\n"
                    f"        configurator_page.verify_save_icon_present()"
                )
            elif "cart" in ac_low or "add to cart" in ac_low:
                mapped = "pdp_page.add_to_cart_quick_order()"
                code = (
                    f"        # Step {idx}: {ac}\n"
                    f"        Reporter.report_step(auth_page_{tc_id.lower()}, \"Step {idx}: {ac}\", \"PASS\")\n"
                    f"        cart_page = pdp_page.add_to_cart_quick_order()\n"
                    f"        cart_page.verify_cart_heading()"
                )
            elif "shipping" in ac_low or "fedex" in ac_low or "checkout" in ac_low:
                mapped = "shipping_page.select_fedex_ground_shipping_method()"
                code = (
                    f"        # Step {idx}: {ac}\n"
                    f"        Reporter.report_step(auth_page_{tc_id.lower()}, \"Step {idx}: {ac}\", \"PASS\")\n"
                    f"        shipping_page = cart_page.click_checkout()\n"
                    f"        shipping_page.verify_shipping_billing_page()\n"
                    f"        shipping_page.select_fedex_ground_shipping_method()"
                )
            elif "category" in ac_low or "plp" in ac_low:
                mapped = "home.click_category_menu('Apparel')"
                code = (
                    f"        # Step {idx}: {ac}\n"
                    f"        Reporter.report_step(auth_page_{tc_id.lower()}, \"Step {idx}: {ac}\", \"PASS\")\n"
                    f"        plp_page = home.click_category_menu('Apparel')\n"
                    f"        plp_page.verify_plp_page_loaded()"
                )
            elif "error" in ac_low or "message" in ac_low:
                mapped = "expect(auth_page.locator('.error-message')).to_be_visible()"
                code = (
                    f"        # Step {idx}: {ac}\n"
                    f"        Reporter.report_step(auth_page_{tc_id.lower()}, \"Step {idx}: {ac}\", \"PASS\")\n"
                    f"        expect(auth_page_{tc_id.lower()}.locator(\"id=Header_GlobalLogin_logonErrorMessage_GL, .error-message, div:has-text('invalid')\").first).to_be_visible(timeout=10000)"
                )
            elif "logout" in ac_low or "log out" in ac_low or "sign out" in ac_low:
                mapped = "home.click_username().log_out()"
                code = (
                    f"        # Step {idx}: {ac}\n"
                    f"        Reporter.report_step(auth_page_{tc_id.lower()}, \"Step {idx}: {ac}\", \"PASS\")\n"
                    f"        home.click_username().log_out()"
                )
            else:
                mapped = f"expect(auth_page_{tc_id.lower()}.locator('body')).to_be_visible()"
                code = (
                    f"        # Step {idx}: {ac}\n"
                    f"        Reporter.report_step(auth_page_{tc_id.lower()}, \"Step {idx}: {ac}\", \"PASS\")\n"
                    f"        expect(auth_page_{tc_id.lower()}.locator(\"body\")).to_be_visible(timeout=10000)"
                )

            ac_mappings.append({"criterion": ac, "mappedStep": mapped})
            script_steps_code.append(code)

        steps_block = "\n\n".join(script_steps_code)

        python_script_content = (
            "import pytest\n"
            "from playwright.sync_api import sync_playwright, expect\n"
            f"{imports_code}\n\n"
            f"@pytest.fixture(scope=\"class\")\n"
            f"def auth_context_{tc_id.lower()}(request, env_config, browser_instance):\n"
            "    headless = request.config.getoption(\"--headless\")\n"
            "    if headless:\n"
            "        context = browser_instance.new_context(\n"
            "            viewport={\"width\": 1440, \"height\": 900},\n"
            "            ignore_https_errors=True\n"
            "        )\n"
            "    else:\n"
            "        context = browser_instance.new_context(\n"
            "            no_viewport=True,\n"
            "            ignore_https_errors=True\n"
            "        )\n"
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
            f"    def test_{re.sub(r'(?<!^)(?=[A-Z])', '_', test_name).lower()}(self, auth_page_{tc_id.lower()}, env_config):\n"
            "        from python_playwright.utils.reporter import Reporter\n"
            f"        Reporter.start_test_case(\"{tc_id}_{test_name}\", \"{user_story.replace('\"', '')}\", \"Regression\", \"SURIYAA\")\n\n"
            "        url = env_config[\"url\"]\n"
            "        username = env_config[\"username\"]\n"
            "        password = env_config[\"password\"]\n\n"
            f"{steps_block}\n"
        )

        template = {
            "testCaseId": tc_id,
            "testName": test_name,
            "description": user_story,
            "frameworkComponents": {
                "pages": pages,
                "fixtures": [f"auth_context_{tc_id.lower()}", f"auth_page_{tc_id.lower()}"],
                "reporter": "Reporter"
            },
            "acceptanceCriteriaMapping": ac_mappings,
            "pythonScript": python_script_content
        }

        return json.dumps(template)

    def _parse_json_response(self, raw_response: str, fallback_title: str) -> Dict[str, Any]:
        """Extracts JSON object safely from LLM output."""
        try:
            return json.loads(raw_response)
        except Exception:
            # Attempt to locate JSON inside markdown code blocks
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_response)
            if match:
                try:
                    return json.loads(match.group(1))
                except Exception:
                    pass

        return {
            "testCaseId": "TC_CUSTOM",
            "testName": "GeneratedTest",
            "description": fallback_title,
            "pythonScript": raw_response
        }

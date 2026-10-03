# 1. Navigate directly to FreeStyle Digital Print Page URL
# 2. Verify FreeStyle Digital Print Page title
# 3. Verify select date field and dropdown
# 4. Verify search field and button
# 5. Verify clear results link
# 6. Verify start new design link

import pytest
import os
from playwright.sync_api import sync_playwright, expect
import re
from python_playwright.pages.home_page import HomePage
from python_playwright.pages.freestyle_digital_print_page import FreeStyleDigitalPrintPage
from python_playwright.utils.reporter import Reporter

from python_playwright.conftest import get_authenticated_context

@pytest.fixture(scope="class")
def auth_context_tc011(request, env_config, browser_instance):
    context = get_authenticated_context(browser_instance, env_config, "tc011_state.json")
    yield context
    context.close()

@pytest.fixture(scope="class")
def auth_page_tc011(auth_context_tc011):
    """
    Yields a single page within the authenticated context for the entire class execution.
    """
    page = auth_context_tc011.new_page()
    yield page
    page.close()

@pytest.mark.usefixtures("auth_page_tc011")
class TestTC011FreeStyleDigitalPrint:
    def test_verify_freestyle_digital_print_page(self, auth_page_tc011, env_config):
        Reporter.start_test_case("TC011_FreeStyleDigitalPrint", "Verify FreeStyle DigitalPrint Validation Elements", "Smoke", "QA")
        
        base_url = env_config["url"].rstrip('/')
        digital_print_url = f"{base_url}/FreeStyleCustomPrintView?catalogId=10601&storeId=10251&langId=-1"
        
        # Navigate to home first to stabilize session cookies, then target URL
        auth_page_tc011.goto(env_config["url"])
        auth_page_tc011.wait_for_load_state("domcontentloaded")
        auth_page_tc011.goto(digital_print_url)
        
        # Wait for page to reach a stable state to prevent flakiness
        try:
            auth_page_tc011.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        auth_page_tc011.wait_for_load_state("domcontentloaded")
            
        # Assert navigation was successful by checking for a specific element or URL
        expect(auth_page_tc011).to_have_url(re.compile(".*FreeStyleCustomPrintView.*", re.IGNORECASE), timeout=15000)
        
        freestyle_page = FreeStyleDigitalPrintPage(auth_page_tc011)
        
        # Execute Validation Steps as per requirements
        freestyle_page.verify_freestyle_digital_print_page_title()
        freestyle_page.verify_select_date_field_and_dropdown()
        freestyle_page.verify_search_field_and_button()
        freestyle_page.verify_clear_results_link()
        freestyle_page.verify_start_new_design_link()

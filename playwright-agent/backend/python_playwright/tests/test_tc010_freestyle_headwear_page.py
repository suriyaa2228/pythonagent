# 1. Navigate directly to FreeStyle Headwear Page URL
# 2. Verify FreeStyle Headwear Page title
# 3. Verify select date field and dropdown
# 4. Verify search field and button
# 5. Verify clear results link
# 6. Verify start new design link

import pytest
import os
from playwright.sync_api import sync_playwright, expect
import re
from python_playwright.pages.home_page import HomePage
from python_playwright.pages.freestyle_headwear_page import FreeStyleHeadwearPage
from python_playwright.utils.reporter import Reporter

@pytest.fixture(scope="class")
def auth_context_tc010(request, env_config, browser_instance):
    """
    Session Reuse (Mandatory): Logs in once and reuses session using Storage State.
    If storage state does not exist, authenticates and creates it.
    """
    url = env_config["url"]
    username = env_config["username"]
    password = env_config["password"]
    
    # Store the authenticated state securely
    config_dir = os.path.join(os.path.dirname(__file__), "..", "config")
    os.makedirs(config_dir, exist_ok=True)
    state_file = os.path.join(config_dir, "tc010_state.json")

    # If the state file doesn't exist, we must authenticate via UI first
    if not os.path.exists(state_file):
        temp_context = browser_instance.new_context(ignore_https_errors=True)
        temp_page = temp_context.new_page()
        temp_page.goto(url)
        
        home = HomePage(temp_page, url)
        home.handle_onetrust_cookie()
        login_page = home.verify_home_page().click_login()
        login_page.enter_username(username) \
            .enter_password(password) \
            .click_login_button()
            
        # Assert login was successful by checking for a specific element or URL
        expect(temp_page.locator("id=Header_GlobalLogin_signOutQuickLinkUser")).to_be_visible(timeout=15000)
            
        temp_context.storage_state(path=state_file)
        temp_page.close()
        temp_context.close()

    # Create a new context pre-hydrated with the authenticated storage state
    context = browser_instance.new_context(
        storage_state=state_file,
        ignore_https_errors=True
    )
    context.set_default_timeout(30000)
    yield context
    context.close()

@pytest.fixture(scope="class")
def auth_page_tc010(auth_context_tc010):
    """
    Yields a single page within the authenticated context for the entire class execution.
    """
    page = auth_context_tc010.new_page()
    yield page
    page.close()

@pytest.mark.usefixtures("auth_page_tc010")
class TestTC010FreeStyleHeadwearPage:
    def test_verify_freestyle_headwear_page(self, auth_page_tc010, env_config):
        Reporter.start_test_case("TC010_FreeStyleHeadwearPage", "Verify FreeStyle Headwear Page elements", "Smoke", "QA")
        
        base_url = env_config["url"].rstrip('/')
        headwear_url = f"{base_url}/FreeStyleHeadwearView?catalogId=10601&storeId=10251&langId=-1"
        
        # Navigate to home first to stabilize session cookies, then target URL
        auth_page_tc010.goto(env_config["url"])
        auth_page_tc010.wait_for_load_state("domcontentloaded")
        auth_page_tc010.goto(headwear_url)
        
        # Wait for page to reach a stable state to prevent flakiness
        try:
            auth_page_tc010.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        auth_page_tc010.wait_for_load_state("domcontentloaded")
        
        # Assert navigation was successful by checking for a specific element or URL
        expect(auth_page_tc010).to_have_url(re.compile(".*FreeStyleHeadwearView.*", re.IGNORECASE), timeout=15000)
        
        freestyle_page = FreeStyleHeadwearPage(auth_page_tc010)
        
        # Execute Validation Steps as per requirements
        freestyle_page.verify_freestyle_headwear_page_title()
        freestyle_page.verify_select_date_field_and_dropdown()
        freestyle_page.verify_search_field_and_button()
        freestyle_page.verify_clear_results_link()
        freestyle_page.verify_start_new_design_link()

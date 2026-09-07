# 1. Navigate to URL and accept cookie banner
# 2. Validate home page load and errors
# 3. Validate header elements
# 4. Validate brand logo
# 5. Validate username dropdown
# 6. Validate mega menus
# 7. Validate direct navigation links
# 8. Validate footer sections

import pytest
import os
from playwright.sync_api import sync_playwright, expect
import re
from python_playwright.pages.home_page import HomePage

@pytest.fixture(scope="class")
def auth_context_tc013(request, env_config, browser_instance):
    """
    Session Reuse (Mandatory): Logs in once and reuses session using Storage State.
    If storage state does not exist, authenticates and creates it.
    """
    url = env_config["url"]
    username = env_config["username"]
    password = env_config["password"]
    
    config_dir = os.path.join(os.path.dirname(__file__), "..", "config")
    os.makedirs(config_dir, exist_ok=True)
    state_file = os.path.join(config_dir, "tc013_state.json")

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

    context = browser_instance.new_context(
        storage_state=state_file,
        ignore_https_errors=True
    )
    context.set_default_timeout(30000)
    yield context
    context.close()

@pytest.fixture(scope="class")
def auth_page_tc013(auth_context_tc013):
    page = auth_context_tc013.new_page()
    yield page
    page.close()

@pytest.mark.usefixtures("auth_page_tc013")
class TestTC013HomePageValidation:
    def test_run_home_page_validation(self, auth_page_tc013, env_config):
        from python_playwright.utils.reporter import Reporter
        Reporter.start_test_case(
            "TC013_HomePageValidation", 
            "Comprehensive Home Page Validation including Header, Navigation, PLP, and Footer", 
            "Regression", 
            "SURIYAA"
        )
        
        url = env_config["url"]
        
        # Explicitly navigate to the home page URL
        auth_page_tc013.goto(url)
        home = HomePage(auth_page_tc013, url)
        home.handle_onetrust_cookie()
        auth_page_tc013.wait_for_timeout(3000)
        
        # Step 1: Home Page Validation
        home.validate_page_load_and_errors()
        
        # Step 2: Header Validation
        home.validate_header_elements()
        
        # Step 3: Brand Logo Validation
        home.validate_brand_logo()
        
        # Step 4: Username Validation
        home.validate_username_dropdown()
        
        # Step 5: Mega Menu Navigation Validation
        home.validate_mega_menus()
        
        # Step 6: Direct Navigation Validation
        home.validate_direct_navigation_links()
        
        # Step 7: Footer Validation
        home.validate_footer_sections()

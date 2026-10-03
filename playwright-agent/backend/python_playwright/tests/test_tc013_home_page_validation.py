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

from python_playwright.conftest import get_authenticated_context

@pytest.fixture(scope="class")
def auth_context_tc013(request, env_config, browser_instance):
    context = get_authenticated_context(browser_instance, env_config, "tc013_state.json")
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

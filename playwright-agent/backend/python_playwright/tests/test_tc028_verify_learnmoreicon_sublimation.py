import os
import pytest
from playwright.sync_api import Page, BrowserContext, expect
from python_playwright.pages.home_page import HomePage
from python_playwright.pages.login_page import LoginPage
from python_playwright.pages.pdp_page import PDPPage
from python_playwright.pages.configurator_page import ConfiguratorPage
from python_playwright.utils.reporter import Reporter
from python_playwright.conftest import get_authenticated_context


@pytest.fixture(scope="class")
def auth_context_tc024(request, env_config, browser_instance):
    context = get_authenticated_context(browser_instance, env_config, "tc026_state.json")
    yield context
    context.close()


@pytest.fixture(scope="class")
def auth_page_tc024(auth_context_tc024):
    page = auth_context_tc024.new_page()
    yield page
    page.close()


class TestSublimationBuilderLearnMoreIcon:
    @pytest.mark.usefixtures("auth_page_tc024")
    def test_learn_more_icon_on_builder(self, auth_page_tc024, env_config):
        page = auth_page_tc024
        url = env_config["url"]
        username = env_config["username"]
        password = env_config["password"]
        
        Reporter.start_test_case("TC024_SublimationBuilderLearnMoreIcon", "Verify the Learn more icon is present on the sublimation builder page", "E2E", "QA")
        
        # AC1: Navigate to homepage
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        home_page = HomePage(page, url)
        home_page.handle_onetrust_cookie()
        home_page.verify_home_page()
        Reporter.report_step(page, "Navigated to homepage", "PASS")
        
        # AC2: Login with valid credentials (verified / logged in via storage state)
        user_icon = page.locator("id=Header_GlobalLogin_signOutQuickLinkUser")
        if not user_icon.is_visible(timeout=3000):
            login_page = LoginPage(page)
            home_page.click_login()
            login_page.enter_username(username)
            login_page.enter_password(password)
            login_page.click_login_button()
        Reporter.report_step(page, "Logged in with valid credentials", "PASS")
        
        # AC3: Search with style 228137
        home_page.search_product("228137")
        Reporter.report_step(page, "Searched for style 228137", "PASS")
        
        # AC4: Navigate to PDP
        pdp_page = PDPPage(page)
        Reporter.report_step(page, "Navigated to PDP", "PASS")
        
        # AC5: Verify PDP is fully loaded
        pdp_page.verify_product_title()
        Reporter.report_step(page, "Verified PDP is fully loaded", "PASS")
        
        # AC6: Verify customise button is present
        pdp_page.verify_customise_button()
        Reporter.report_step(page, "Verified customise button is present", "PASS")
        
        # AC7: Click customize button
        pdp_page.click_customize_button()
        Reporter.report_step(page, "Clicked customize button", "PASS")
        
        # AC8: Navigate to builder
        configurator_page = ConfiguratorPage(page)
        Reporter.report_step(page, "Navigated to builder", "PASS")
        
        # AC9: Verify the builder is loaded properly
        configurator_page.verify_builder_loaded()
        Reporter.report_step(page, "Verified builder is loaded properly", "PASS")
        
        # AC10: Check the Learn more icon is present on the builder page
        configurator_page.verify_learn_more_icon()
        Reporter.report_step(page, "Verified Learn more icon is present on the builder page", "PASS")
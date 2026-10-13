import pytest
from playwright.sync_api import Page, expect
from python_playwright.conftest import get_authenticated_context
from python_playwright.pages.home_page import HomePage
from python_playwright.pages.pdp_page import PDPPage
from python_playwright.utils.reporter import Reporter


class TestVerifyViewIconsOnPDP:
    @pytest.fixture(scope="class")
    def auth_context_tc024(self, request, env_config, browser_instance):
        context = get_authenticated_context(browser_instance, env_config, "tc024_state.json")
        yield context
        context.close()

    @pytest.fixture(scope="class")
    def auth_page_tc024(self, auth_context_tc024):
        page = auth_context_tc024.new_page()
        yield page
        page.close()

    @pytest.mark.usefixtures("auth_page_tc024")
    def test_verify_view_icons_on_pdp(self, auth_page_tc024, env_config):
        Reporter.start_test_case("TC024_VerifyViewIconsOnPDP", "Verify that view spec, view inventory, and view sizing info buttons are present on the PDP page for style 6117", "E2E", "QA")
        
        # AC1: Navigate to homepage
        auth_page_tc024.goto(env_config["url"], wait_until="domcontentloaded", timeout=30000)
        home_page = HomePage(auth_page_tc024, env_config["url"])
        home_page.handle_onetrust_cookie()
        Reporter.report_step(auth_page_tc024, "Navigated to homepage and handled cookies", "PASS")
        
        # AC2: Login with valid credentials (handled by authenticated context)
        Reporter.report_step(auth_page_tc024, "Logged in with valid credentials via authenticated context", "PASS")
        
        # AC3: Search with style 6117
        home_page.search_product("6117")
        Reporter.report_step(auth_page_tc024, "Searched for style 6117", "PASS")
        
        # AC4: Navigate to PDP
        pdp_page = PDPPage(auth_page_tc024)
        Reporter.report_step(auth_page_tc024, "Navigated to PDP page", "PASS")
        
        # AC5: Verify the PDP is fully loaded
        pdp_page.verify_product_title()
        Reporter.report_step(auth_page_tc024, "Verified PDP is fully loaded", "PASS")
        
        # AC6: Verify view spec button is present
        pdp_page.verify_view_spec_link()
        Reporter.report_step(auth_page_tc024, "Verified view spec button is present", "PASS")
        
        # AC7: Verify view Inventory button is present
        pdp_page.verify_view_inventory_link()
        Reporter.report_step(auth_page_tc024, "Verified view inventory button is present", "PASS")
        
        # AC8: Verify view sizing info button is present
        pdp_page.verify_view_sizing_info_link()
        Reporter.report_step(auth_page_tc024, "Verified view sizing info button is present", "PASS")
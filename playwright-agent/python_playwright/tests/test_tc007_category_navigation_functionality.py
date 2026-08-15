import pytest
import os
from playwright.sync_api import sync_playwright, expect
import re
from python_playwright.pages.home_page import HomePage
from python_playwright.utils.reporter import Reporter

@pytest.fixture(scope="class")
def auth_context_tc007(request, env_config, browser_instance):
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
    state_file = os.path.join(config_dir, "tc007_state.json")

    # If the state file doesn't exist, we must authenticate via UI first
    if not os.path.exists(state_file):
        temp_context = browser_instance.new_context(ignore_https_errors=True, no_viewport=True)
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
        ignore_https_errors=True,
        no_viewport=True
    )
    context.set_default_timeout(30000)
    yield context
    context.close()

@pytest.fixture(scope="class")
def auth_page_tc007(auth_context_tc007):
    """
    Yields a single page within the authenticated context for the entire class execution.
    """
    page = auth_context_tc007.new_page()
    yield page
    page.close()


@pytest.mark.usefixtures("auth_page_tc007")
class TestTC007CategoryNavigationFunctionality:
    def test_category_navigation(self, auth_page_tc007, env_config):
        Reporter.start_test_case("TC007_CategoryNavigationFunctionality", "Verify Category Navigation functionality", "E2E", "QA")
        
        url = env_config["url"]
        
        # 1. Navigate to home page and validate
        try:
            auth_page_tc007.goto(url, wait_until="commit", timeout=120000)
        except Exception as e:
            print(f"[WARNING] Navigation timed out: {e}. Retrying navigation with domcontentloaded...")
            auth_page_tc007.goto(url, wait_until="domcontentloaded", timeout=120000)
            
        try:
            auth_page_tc007.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception:
            pass

        home_page = HomePage(auth_page_tc007, url)
        home_page.verify_home_page()
        
        # 2. Validate homepage logo is present
        home_page.validate_brand_logo()
        
        # 3. Mouse hover on BRANDS
        home_page.hover_mega_menu("BRANDS")
        
        # 4. Wait for dropdown and assert OUR BRANDS and PARTNER BRANDS
        home_page.verify_brands_dropdown()
        
        # 5. Click Augusta sportswear and verify navigation
        plp_page = home_page.click_sub_category_in_mega_menu("Augusta sportswear")
        plp_page.verify_url("augusta-1")
        plp_page.verify_page_heading("AUGUSTA SPORTSWEAR")
        
        # 6. Click the brand logo on top left
        home_page = plp_page.click_brand_logo()
        
        # 7. Wait for navigation to homepage and assert
        home_page.verify_home_page()
        
        # 8. Again mouse hover on the brands
        home_page.hover_mega_menu("BRANDS")
        
        # 9. Click Babe Ruth from the PARTNER BRANDS section
        plp_page = home_page.click_sub_category_in_mega_menu("Babe Ruth")
        
        # 10. Wait for navigation to babe-ruth, verify title and products
        plp_page.verify_url("babe-ruth")
        plp_page.verify_page_heading("Babe Ruth")
        
        # Wait for the page and product grid to fully load
        try:
            auth_page_tc007.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        auth_page_tc007.wait_for_timeout(3000)
        
        plp_page.validate_product_grid()
        
        # 11. Click the brand logo on top left
        home_page = plp_page.click_brand_logo()
        
        # 12. Wait for navigation to homepage and assert
        home_page.verify_home_page()

import pytest
import os
from playwright.sync_api import sync_playwright, expect
import re
from python_playwright.pages.home_page import HomePage
from python_playwright.utils.reporter import Reporter

@pytest.fixture(scope="class")
def auth_context_tc006(request, env_config, browser_instance):
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
    state_file = os.path.join(config_dir, "tc006_state.json")

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
def auth_page_tc006(auth_context_tc006):
    """
    Yields a single page within the authenticated context for the entire class execution.
    """
    page = auth_context_tc006.new_page()
    yield page
    page.close()


@pytest.mark.usefixtures("auth_page_tc006")
class TestTC006SearchFunctionality:
    def test_search_functionality(self, auth_page_tc006, env_config):
        Reporter.start_test_case("TC006_SearchFunctionality", "Verify Search functionality for different products", "E2E", "QA")
        
        url = env_config["url"]
        
        # 1. Navigate to home page
        try:
            auth_page_tc006.goto(url, wait_until="commit", timeout=120000)
        except Exception as e:
            print(f"[WARNING] Navigation timed out: {e}. Retrying navigation with domcontentloaded...")
            auth_page_tc006.goto(url, wait_until="domcontentloaded", timeout=120000)
            
        try:
            auth_page_tc006.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception:
            pass

        home_page = HomePage(auth_page_tc006, url)
        home_page.verify_home_page()
        
        # 2. Search 7001
        pdp_page = home_page.search_product("7001")
        pdp_page.verify_url_contains("augusta-pursuit-polo-7001")
        pdp_page.verify_page_headings(["Augusta", "Augusta Sportswear", "Pursuit Polo"])
        
        # 3. Search 228118
        # Since we are already on the PDP page, we can use the search bar again.
        # We can just instantiate HomePage and use its search_product method because the search bar is global.
        HomePage(auth_page_tc006, url).search_product("228118")
        pdp_page.verify_url_contains("freestyle-sublimated-turbo-reversible-basketball-jersey-cut-228118")
        pdp_page.verify_page_headings(["Holloway", "FreeStyle Sublimated Turbo Reversible Basketball Jersey"])
        
        # 4. Search 404F
        HomePage(auth_page_tc006, url).search_product("404F")
        pdp_page.verify_url_contains("pacific-headwear-trucker-flexfit-cap-404f")
        pdp_page.verify_page_headings(["Pacific Headwear", "Trucker Flexfit® Cap"])
        
        # 5. Search 6951
        HomePage(auth_page_tc006, url).search_product("6951")
        pdp_page.verify_url_contains("augusta-youth-all-day-core-basic-50-50-tee-6951")
        pdp_page.verify_page_headings(["Augusta Sportswear", "Youth All-Day Core Basic 50/50 Tee"])

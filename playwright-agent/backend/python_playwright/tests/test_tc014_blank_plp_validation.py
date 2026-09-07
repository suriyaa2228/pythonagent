# 1. Navigate to URL and accept cookie banner
# 2. For each PLP link, navigate to the PLP page
# 3. Validate sorting options
# 4. Validate filters
# 5. Get a random product
# 6. Validate product card elements
# 7. Hover and click Quick Order on the product
# 8. Validate Quick Order popup features
# 9. Add product to cart from Quick Order popup
# 10. Validate 'Items Added to Your Cart' popup and navigate to cart
# 11. Verify Cart page heading
# 12. Clear the cart
# 13. Validate empty cart and Continue Shopping button

import pytest
import os
from playwright.sync_api import sync_playwright, expect
import re
from python_playwright.pages.home_page import HomePage
from python_playwright.pages.plp_page import PLPPage

@pytest.fixture(scope="class")
def auth_context_tc014(request, env_config, browser_instance):
    """
    Session Reuse (Mandatory): Logs in once and reuses session using Storage State.
    If storage state does not exist, authenticates and creates it.
    """
    url = env_config["url"]
    username = env_config["username"]
    password = env_config["password"]
    
    config_dir = os.path.join(os.path.dirname(__file__), "..", "config")
    os.makedirs(config_dir, exist_ok=True)
    state_file = os.path.join(config_dir, "tc014_state.json")

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
def auth_page_tc014(auth_context_tc014):
    page = auth_context_tc014.new_page()
    yield page
    page.close()

@pytest.mark.usefixtures("auth_page_tc014")
class TestTC014BlankPLPValidation:
    def test_run_blank_plp_validation(self, auth_page_tc014, env_config):
        from python_playwright.utils.reporter import Reporter
        Reporter.start_test_case(
            "TC014_BlankPLPValidation", 
            "Blank PLP Validations including Quick Order, Product Cards, and Cart clearing", 
            "Regression", 
            "SURIYAA"
        )
        
        url = env_config["url"]
        
        # We start with the authenticated session
        auth_page_tc014.goto(url)
        home = HomePage(auth_page_tc014, url)
        home.handle_onetrust_cookie()
        auth_page_tc014.wait_for_timeout(3000)
        
        # Links to validate
        plp_links = [
            "https://stage.momentecbrands.com/augusta-1",
            "https://stage.momentecbrands.com/badger-sport",
            "https://stage.momentecbrands.com/alleson-1",
            "https://stage.momentecbrands.com/c2-sport-1"
        ]
        
        for plp_link in plp_links:
            from python_playwright.utils.reporter import Reporter
            Reporter.report_step(auth_page_tc014, f"====== TESTING PLP LINK: {plp_link} ======", "info", snap=False)
            
            auth_page_tc014.goto(plp_link)
            auth_page_tc014.wait_for_load_state("domcontentloaded")
            auth_page_tc014.wait_for_timeout(2000)
            
            plp = PLPPage(auth_page_tc014)
            
            # Validate sorting and filters
            plp.validate_sort_by_price()
            plp.validate_category_and_multiple_filters()
            
            # Get a random product
            product = plp.get_random_product()
            auth_page_tc014.wait_for_timeout(3000)
            
            # Validate product card elements (hover for Quick Order, logo, thumbnails, Style ID, Price)
            # including "selected thumbnail is showing on the Hero image"
            plp.validate_product_card_elements(product)
            auth_page_tc014.wait_for_timeout(3000)
            
            # Hover and trigger Quick Order Pop-up
            plp.hover_and_click_quick_order(product)
            auth_page_tc014.wait_for_timeout(3000)
            
            # Validate Quick Order popup features (thumbnails, colors, show/hide price, quantity box, similar style, view details)
            plp.validate_quick_order_popup()
            auth_page_tc014.wait_for_timeout(3000)
            
            # Add to cart from Quick Order Pop-up
            plp.add_to_cart_from_quick_order()
            auth_page_tc014.wait_for_timeout(3000)
            
            # Validate ITEMS ADDED TO YOUR CART popup and navigate to cart
            cart = plp.validate_items_added_popup_and_navigate()
            auth_page_tc014.wait_for_timeout(3000)
            
            # Assert navigation to cart was successful by checking for a specific element or URL
            expect(auth_page_tc014).to_have_url(re.compile(".*(cart|CartView|AjaxOrderItemDisplayView).*", re.IGNORECASE), timeout=15000)
            
            # Verify Cart page, clear it and navigate back to Home
            cart.verify_cart_heading()
            auth_page_tc014.wait_for_timeout(3000)
            
            cart.clear_cart()
            auth_page_tc014.wait_for_timeout(3000)
            
            home_page = cart.validate_empty_cart_continue_shopping()
            auth_page_tc014.wait_for_timeout(3000)

# 1. Navigate to URL and accept cookie banner
# 2. Navigate directly to Custom Sublimation Page URL
# 3. Verify Custom Sublimation Page title
# 4. Click customize on a specific product
# 5. Accept cookies in Configurator
# 6. Verify Design tab is open, 3D image is showing, and design lines are showing
# 7. Select a design
# 8. Click Next Color
# 9. Verify color dropdowns and select color
# 10. Click Next Text and Logo
# 11. Add text decoration and art decoration
# 12. Click Next Roster
# 13. Verify roster fields and add size
# 14. Click Next Summary
# 15. Verify summary info
# 16. Add to cart
# 17. Fill Cart Popup with details (Name, Email, Phone)
# 18. Verify Cart heading
# 19. Click Checkout
# 20. Verify Shipping and Billing page
# 21. Select FedEx Ground shipping method
# 22. Click Review and Submit
# 23. Click Place Order
# 24. Get order number from Thank You page

import pytest
import os
from playwright.sync_api import sync_playwright, expect
import re
from python_playwright.pages.home_page import HomePage
from python_playwright.pages.custom_sublimation_page import CustomSublimationPage
from python_playwright.pages.configurator_page import ConfiguratorPage
from python_playwright.utils.reporter import Reporter

@pytest.fixture(scope="class")
def auth_context_tc012(request, env_config, browser_instance):
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
    state_file = os.path.join(config_dir, "tc012_state.json")

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
def auth_page_tc012(auth_context_tc012):
    """
    Yields a single page within the authenticated context for the entire class execution.
    """
    page = auth_context_tc012.new_page()
    yield page
    page.close()

@pytest.mark.usefixtures("auth_page_tc012")
class TestTC012SublimationOrderPlacing:
    def test_sublimation_order_placing_flow(self, auth_page_tc012, env_config):
        Reporter.start_test_case("TC012_SublimationOrderPlacing", "Verify Sublimation Order Placing flow", "E2E", "QA")
        
        base_url = env_config["url"].rstrip('/')
        sublimation_url = f"{base_url}/custom-sublimation"
        
        # Clear cart first
        from python_playwright.pages.cart_page import CartPage
        CartPage(auth_page_tc012).clear_cart()
        
        try:
            auth_page_tc012.goto(sublimation_url, wait_until="commit", timeout=120000)
        except Exception as e:
            print(f"[WARNING] Navigation timed out: {e}. Retrying navigation with domcontentloaded...")
            auth_page_tc012.goto(sublimation_url, wait_until="domcontentloaded", timeout=120000)
            
        try:
            auth_page_tc012.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception:
            pass
        
        # 1. Custom Sublimation Page
        custom_sublimation_page = CustomSublimationPage(auth_page_tc012)
        custom_sublimation_page.verify_custom_sublimation_page_title()
        
        custom_sublimation_page.verify_products_listed()
        custom_sublimation_page.verify_customize_button_on_hover()
        
        # Click customize on Style # 227232 -> Navigates to Configurator
        configurator_page = custom_sublimation_page.click_customize_on_product("227232")
        
        configurator_page.verify_configurator_loaded()
        
        # Accept cookies
        configurator_page.accept_cookies()
        
        # 2. Configurator Flow
        # Design Tab
        configurator_page.verify_design_tab_is_open()
        configurator_page.verify_3d_image_showing()
        configurator_page.verify_design_lines_showing()
        configurator_page.select_design()
        
        try:
            print("Taking screenshot of the Configurator page...")
            configurator_page.page.screenshot(path="configurator_screenshot.png", full_page=True)
            print("Screenshot saved to configurator_screenshot.png")
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            
        configurator_page.click_next_color()
        configurator_page.verify_navigated_to_colors_tab()
        
        # Color Tab
        configurator_page.verify_color_dropdowns_and_select()
        configurator_page.click_next_text_and_logo()
        
        # Text & Logo Tab
        configurator_page.add_text_decoration(text="TEST")
        configurator_page.add_art_decoration()
        configurator_page.click_next_roster()
        
        # Roster Tab
        configurator_page.verify_roster_fields_and_add_size()
        configurator_page.click_next_summary()
        
        # Summary Tab
        configurator_page.verify_summary_info()
        configurator_page.add_to_cart()
        
        # Fill Cart Popup
        name = "test order donot ship"
        email = "suriyaa2228@gmail.com"
        phone = "2323232323"
        cart_page = configurator_page.fill_cart_popup(name, email, phone)
        
        # 3. Checkout Flow
        cart_page.verify_cart_heading()
        shipping_billing_page = cart_page.click_checkout()
        
        # Assert navigation to shipping page was successful by checking for a specific element or URL
        expect(auth_page_tc012).to_have_url(re.compile(".*(checkout|shipping|OrderShipping).*", re.IGNORECASE), timeout=15000)
        
        shipping_billing_page.verify_shipping_billing_page()
        # Ensure we pick a shipping method just in case
        shipping_billing_page.click_shipping_methods_dd()
        shipping_billing_page.verify_only_fedex_ground_in_dropdown()
        shipping_billing_page.select_fedex_ground_shipping_method()
        
        review_submit_page = shipping_billing_page.click_review_and_submit()
        
        # Review and Submit
        thank_you_page = review_submit_page.click_place_order()
        
        # Assert order was placed successfully by checking for a specific element or URL
        expect(auth_page_tc012).to_have_url(re.compile(".*(OrderOKView|ThankYou|OrderShippingBillingConfirmationView).*", re.IGNORECASE), timeout=30000)
        
        # Capture Order Number
        thank_you_page.get_order_number()

# 1. Navigate to URL and accept cookie banner
# 2. Click Brand Logo and verify home page
# 3. Search for product "295000"
# 4. Verify search product in PDP page
# 5. Select color black
# 6. Verify placeholder
# 7. Enter quantity
# 8. Add to cart
# 9. Verify mini shop cart
# 10. Click Go to Cart
# 11. Verify Cart heading
# 12. Click Checkout
# 13. Verify Shipping and Billing page
# 14. Click Shipping Methods dropdown
# 15. Select FedEx Ground shipping method
# 16. Verify FedEx Ground charge
# 17. Navigate back to cart
# 18. Update quantity in cart to "120"
# 19. Click Checkout
# 20. Verify Shipping and Billing page
# 21. Click Shipping Methods dropdown
# 22. Select FedEx Ground shipping method
# 23. Verify FedEx Ground is free
# 24. Navigate back to cart
# 25. Clear cart

import pytest
import os
from playwright.sync_api import sync_playwright, expect
import re
from python_playwright.pages.home_page import HomePage
from python_playwright.pages.pdp_page import PDPPage
from python_playwright.pages.cart_page import CartPage
from python_playwright.pages.shipping_billing_page import ShippingAndBillingPage

@pytest.fixture(scope="class")
def auth_context_tc004(request, env_config, browser_instance):
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
    state_file = os.path.join(config_dir, "tc004_state.json")

    # If the state file doesn't exist, we must authenticate via UI first
    if not os.path.exists(state_file):
        temp_context = browser_instance.new_context(ignore_https_errors=True)
        temp_page = temp_context.new_page()
        temp_page.goto(url)
        
        home = HomePage(temp_page, url)
        home.handle_onetrust_cookie()
        # Clear cart to ensure no backordered items are present
        try:
            temp_page.goto(url + "AjaxOrderItemDisplayView?catalogId=10601&langId=-1&storeId=10251")
            from python_playwright.pages.cart_page import CartPage
            cart = CartPage(temp_page)
            cart.clear_cart()
        except Exception:
            pass
        
        temp_page.goto(url)

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
def auth_page_tc004(auth_context_tc004):
    """
    Yields a single page within the authenticated context for the entire class execution.
    """
    page = auth_context_tc004.new_page()
    yield page
    page.close()

@pytest.mark.usefixtures("auth_page_tc004")
class TestTC004VerifyShippingFedexGroundValidation:
    def test_verify_shipping_charge(self, auth_page_tc004, env_config):
        from python_playwright.utils.reporter import Reporter
        Reporter.start_test_case("TC004_VerifyShippingFedexGroundValidation", "Verify FEDEX Ground shipping is showing the correct price or not", "Smoke", "SURIYAA")
        
        url = env_config["url"]
        
        auth_page_tc004.goto(url)
        home = HomePage(auth_page_tc004, url)
        home.handle_onetrust_cookie()
        # Clear cart to ensure no backordered items are present
        try:
            auth_page_tc004.goto(url + "AjaxOrderItemDisplayView?catalogId=10601&langId=-1&storeId=10251")
            from python_playwright.pages.cart_page import CartPage
            cart = CartPage(auth_page_tc004)
            cart.clear_cart()
        except Exception:
            pass
        
        auth_page_tc004.goto(url)

        
        # Already logged in, just search product
        home.click_brand_logo() \
            .verify_home_page() \
            .search_product("295000")
            
        # Product detail page actions
        pdp = PDPPage(auth_page_tc004)
        pdp.verify_search_product() \
            .select_color_black() \
            .verify_place_holder("295000") \
            .enter_quantity("295000") \
            .add_to_cart() \
            .verify_mini_shop_cart() \
            .click_go_to_cart()
            
        # Assert navigation to cart was successful by checking for a specific element or URL
        expect(auth_page_tc004).to_have_url(re.compile(".*(cart|CartView|AjaxOrderItemDisplayView).*", re.IGNORECASE), timeout=15000)
            
        # Go to cart and click checkout
        cart = CartPage(auth_page_tc004)
        cart.verify_cart_heading() \
            .click_checkout()
            
        # Assert navigation to shipping page was successful by checking for a specific element or URL
        expect(auth_page_tc004).to_have_url(re.compile(".*(checkout|shipping|OrderShipping).*", re.IGNORECASE), timeout=15000)
            
        # Select FedEx Ground and verify charge (below threshold)
        shipping = ShippingAndBillingPage(auth_page_tc004)
        shipping.verify_shipping_billing_page() \
            .click_shipping_methods_dd() \
            .select_fedex_ground_shipping_method() \
            .verify_fedex_ground_charge() \
            .navigate_back_to_cart()
            
        # Update quantity in cart to exceed free shipping threshold
        cart.update_qty_txt_fld("120") \
            .click_checkout()
            
        # Select FedEx Ground and verify FREE shipping
        shipping.verify_shipping_billing_page() \
            .click_shipping_methods_dd() \
            .select_fedex_ground_shipping_method() \
            .verify_fedex_ground_free() \
            .navigate_back_to_cart()
            
        # Clear cart for cleanliness
        cart.clear_cart()


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
# 12. Update quantity to "2" in cart
# 13. Click Checkout
# 14. Verify Shipping and Billing page
# 15. Click Shipping Methods dropdown
# 16. Select FedEx 2Day shipping method
# 17. Verify FedEx 2Day charge
# 18. Navigate back to cart
# 19. Clear cart

import pytest
import os
from playwright.sync_api import sync_playwright, expect
import re
from python_playwright.pages.home_page import HomePage
from python_playwright.pages.pdp_page import PDPPage
from python_playwright.pages.cart_page import CartPage
from python_playwright.pages.shipping_billing_page import ShippingAndBillingPage

@pytest.fixture(scope="class")
def auth_context_tc005(request, env_config, browser_instance):
    """
    Session Reuse (Mandatory): Logs in once and reuses session using Storage State.
    If storage state does not exist, authenticates and creates it.
    """
    url = env_config["url"]
    username = env_config["username"]
    password = env_config["password"]
    
    config_dir = os.path.join(os.path.dirname(__file__), "..", "config")
    os.makedirs(config_dir, exist_ok=True)
    state_file = os.path.join(config_dir, "tc005_state.json")

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

    context = browser_instance.new_context(
        storage_state=state_file,
        ignore_https_errors=True
    )
    context.set_default_timeout(30000)
    yield context
    context.close()

@pytest.fixture(scope="class")
def auth_page_tc005(auth_context_tc005):
    page = auth_context_tc005.new_page()
    yield page
    page.close()

@pytest.mark.usefixtures("auth_page_tc005")
class TestTC005VerifyShippingFedex2dayValidation:
    def test_verify_shipping_charge(self, auth_page_tc005, env_config):
        from python_playwright.utils.reporter import Reporter
        Reporter.start_test_case("TC005_VerifyShippingFedex2dayValidation", "Verify Fedex 2 day shipping method", "Smoke", "SURIYAA")
        
        url = env_config["url"]
        
        auth_page_tc005.goto(url)
        home = HomePage(auth_page_tc005, url)
        home.handle_onetrust_cookie()
        # Clear cart to ensure no backordered items are present
        try:
            auth_page_tc005.goto(url + "AjaxOrderItemDisplayView?catalogId=10601&langId=-1&storeId=10251")
            from python_playwright.pages.cart_page import CartPage
            cart = CartPage(auth_page_tc005)
            cart.clear_cart()
        except Exception:
            pass
        
        auth_page_tc005.goto(url)

        
        # Already logged in, search product
        home.click_brand_logo() \
            .verify_home_page() \
            .search_product("295000")
            
        pdp = PDPPage(auth_page_tc005)
        pdp.verify_search_product() \
            .select_color_black() \
            .verify_place_holder("295000") \
            .enter_quantity("295000") \
            .add_to_cart() \
            .verify_mini_shop_cart() \
            .click_go_to_cart()
            
        # Assert navigation to cart was successful by checking for a specific element or URL
        expect(auth_page_tc005).to_have_url(re.compile(".*(cart|CartView|AjaxOrderItemDisplayView).*", re.IGNORECASE), timeout=15000)
            
        cart = CartPage(auth_page_tc005)
        cart.verify_cart_heading() \
            .update_qty_txt_fld("2") \
            .click_checkout()
            
        # Assert navigation to shipping page was successful by checking for a specific element or URL
        expect(auth_page_tc005).to_have_url(re.compile(".*(checkout|shipping|OrderShipping).*", re.IGNORECASE), timeout=15000)
            
        shipping = ShippingAndBillingPage(auth_page_tc005)
        shipping.verify_shipping_billing_page() \
            .click_shipping_methods_dd() \
            .select_fedex_2day() \
            .verify_fedex_2day_charge() \
            .navigate_back_to_cart()
            
        cart.clear_cart()

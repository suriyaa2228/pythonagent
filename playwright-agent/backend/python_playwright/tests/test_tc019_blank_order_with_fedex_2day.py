# 1. Navigate to URL and accept cookie banner
# 2. Verify home page
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
# 15. Select FedEx 2Day shipping method
# 16. Click Review and Submit
# 17. Click Place Order on Review Submit page
# 18. Get order number from Thank You page

import pytest
import os
from playwright.sync_api import sync_playwright, expect
import re
from python_playwright.pages.home_page import HomePage
from python_playwright.pages.pdp_page import PDPPage
from python_playwright.pages.cart_page import CartPage
from python_playwright.pages.shipping_billing_page import ShippingAndBillingPage
from python_playwright.pages.review_submit_page import ReviewSubmitPage
from python_playwright.pages.thank_you_page import ThankYouPage

@pytest.fixture(scope="class")
def auth_context_tc008(request, env_config, browser_instance):
    """
    Session Reuse (Mandatory): Logs in once and reuses session using Storage State.
    If storage state does not exist, authenticates and creates it.
    """
    url = env_config["url"]
    username = env_config["username"]
    password = env_config["password"]
    
    config_dir = os.path.join(os.path.dirname(__file__), "..", "config")
    os.makedirs(config_dir, exist_ok=True)
    state_file = os.path.join(config_dir, "tc008_state.json")

    if not os.path.exists(state_file):
        temp_context = browser_instance.new_context(ignore_https_errors=True)
        temp_page = temp_context.new_page()
        temp_page.goto(url)
        
        home = HomePage(temp_page, url)
        home.handle_onetrust_cookie()
        # Clear cart to ensure no backordered items are present
        try:
            auth_page_tc008.goto(url + "AjaxOrderItemDisplayView?catalogId=10601&langId=-1&storeId=10251")
            from python_playwright.pages.cart_page import CartPage
            cart = CartPage(auth_page_tc008)
            cart.clear_cart()
        except Exception:
            pass
        
        auth_page_tc008.goto(url)

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
def auth_page_tc008(auth_context_tc008):
    page = auth_context_tc008.new_page()
    yield page
    page.close()

@pytest.mark.usefixtures("auth_page_tc008")
class TestTC008BlankOrderWithFedEx2Day:
    def test_place_order(self, auth_page_tc008, env_config):
        from python_playwright.utils.reporter import Reporter
        Reporter.start_test_case("TC008_BlankOrderWithFedEx2Day", "Verify able to place blank order with FedEx 2 day Shipping method", "Smoke", "SURIYAA")
        
        url = env_config["url"]
        
        auth_page_tc008.goto(url)
        home = HomePage(auth_page_tc008, url)
        home.handle_onetrust_cookie()
        # Clear cart to ensure no backordered items are present
        try:
            auth_page_tc008.goto(url + "AjaxOrderItemDisplayView?catalogId=10601&langId=-1&storeId=10251")
            from python_playwright.pages.cart_page import CartPage
            cart = CartPage(auth_page_tc008)
            cart.clear_cart()
        except Exception:
            pass
        
        auth_page_tc008.goto(url)

        
        # Already logged in, search product
        home.verify_home_page() \
            .search_product("295000")
            
        pdp = PDPPage(auth_page_tc008)
        pdp.verify_search_product() \
            .select_color_black() \
            .verify_place_holder("295000") \
            .enter_quantity("295000") \
            .add_to_cart() \
            .verify_mini_shop_cart() \
            .click_go_to_cart()
            
        # Assert navigation to cart was successful by checking for a specific element or URL
        expect(auth_page_tc008).to_have_url(re.compile(".*(cart|CartView|AjaxOrderItemDisplayView).*", re.IGNORECASE), timeout=15000)
            
        cart = CartPage(auth_page_tc008)
        cart.verify_cart_heading() \
            .click_checkout()
            
        # Assert navigation to shipping page was successful by checking for a specific element or URL
        expect(auth_page_tc008).to_have_url(re.compile(".*(checkout|shipping|OrderShipping).*", re.IGNORECASE), timeout=15000)
            
        shipping = ShippingAndBillingPage(auth_page_tc008)
        shipping.verify_shipping_billing_page() \
            .click_shipping_methods_dd() \
            .select_fedex_2day() \
            .click_review_and_submit()
            
        review = ReviewSubmitPage(auth_page_tc008)
        review.click_place_order()
        
        # Assert order was placed successfully by checking for a specific element or URL
        expect(auth_page_tc008).to_have_url(re.compile(".*(OrderOKView|ThankYou|OrderShippingBillingConfirmationView).*", re.IGNORECASE), timeout=30000)
        
        thank_you = ThankYouPage(auth_page_tc008)
        thank_you.get_order_number()

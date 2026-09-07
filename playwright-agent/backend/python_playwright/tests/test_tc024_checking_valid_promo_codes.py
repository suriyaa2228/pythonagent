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
# 11. Read promo codes from input promo code folder and validate each code on Cart page
# 12. Save valid promo codes (discount > $0) into valid promo code folder
# 13. Save invalid promo codes (error popup or discount = $0) into invalid promo code folder

import pytest
import os
import re
from playwright.sync_api import expect
from python_playwright.pages.home_page import HomePage
from python_playwright.pages.pdp_page import PDPPage
from python_playwright.pages.cart_page import CartPage
from python_playwright.utils.reporter import Reporter

@pytest.fixture(scope="class")
def auth_context_tc024(request, env_config, browser_instance):
    """
    Session Reuse (Mandatory): Logs in once and reuses session using Storage State.
    If storage state does not exist or is expired, authenticates and updates it.
    """
    url = env_config["url"]
    username = env_config["username"]
    password = env_config["password"]
    
    config_dir = os.path.join(os.path.dirname(__file__), "..", "config")
    os.makedirs(config_dir, exist_ok=True)
    state_file = os.path.join(config_dir, "tc006_state.json")

    # Helper function to perform UI login
    def perform_login():
        temp_context = browser_instance.new_context(ignore_https_errors=True)
        temp_page = temp_context.new_page()
        temp_page.goto(url)
        
        home = HomePage(temp_page, url)
        home.handle_onetrust_cookie()
        
        login_page = home.verify_home_page().click_login()
        login_page.enter_username(username) \
            .enter_password(password) \
            .click_login_button()
            
        expect(temp_page.locator("id=Header_GlobalLogin_signOutQuickLinkUser")).to_be_visible(timeout=15000)
            
        temp_context.storage_state(path=state_file)
        temp_page.close()
        temp_context.close()

    if not os.path.exists(state_file):
        perform_login()
    else:
        # Verify if existing state file is still valid
        check_context = browser_instance.new_context(storage_state=state_file, ignore_https_errors=True)
        check_page = check_context.new_page()
        try:
            check_page.goto(url, timeout=15000)
            sign_out = check_page.locator("id=Header_GlobalLogin_signOutQuickLinkUser")
            if not sign_out.is_visible(timeout=5000):
                print("[INFO] Session expired in state_file. Re-authenticating...")
                check_page.close()
                check_context.close()
                perform_login()
            else:
                check_page.close()
                check_context.close()
        except Exception:
            check_page.close()
            check_context.close()
            perform_login()

    context = browser_instance.new_context(
        storage_state=state_file,
        ignore_https_errors=True
    )
    context.set_default_timeout(30000)
    yield context
    context.close()


@pytest.fixture(scope="class")
def auth_page_tc024(auth_context_tc024):
    page = auth_context_tc024.new_page()
    yield page
    page.close()

@pytest.mark.usefixtures("auth_page_tc024")
class TestTC024CheckingValidPromoCodes:
    def test_checking_valid_promo_codes(self, auth_page_tc024, env_config):
        Reporter.start_test_case("TC024_CheckingValidPromoCodes", "Verify and categorize promo codes as valid or invalid on Cart page", "Regression", "SURIYAA")
        
        url = env_config["url"]
        
        # 1. Navigate to URL and accept cookie banner
        auth_page_tc024.goto(url)
        home = HomePage(auth_page_tc024, url)
        home.handle_onetrust_cookie()
        
        # Clear cart to start with a fresh state
        try:
            auth_page_tc024.goto(url + "AjaxOrderItemDisplayView?catalogId=10601&langId=-1&storeId=10251")
            cart = CartPage(auth_page_tc024)
            cart.clear_cart()
        except Exception:
            pass
            
        auth_page_tc024.goto(url)

        # 2. Verify home page
        # 3. Search for product "295000"
        home.verify_home_page() \
            .search_product("295000")
            
        pdp = PDPPage(auth_page_tc024)
        # 4. Verify search product in PDP page
        # 5. Select color black
        # 6. Verify placeholder
        # 7. Enter quantity
        # 8. Add to cart
        # 9. Verify mini shop cart
        # 10. Click Go to Cart
        pdp.verify_search_product() \
            .select_color_black() \
            .verify_place_holder("295000") \
            .enter_quantity("295000") \
            .add_to_cart() \
            .verify_mini_shop_cart() \
            .click_go_to_cart()
            
        # Assert navigation to cart was successful
        expect(auth_page_tc024).to_have_url(re.compile(".*(cart|CartView|AjaxOrderItemDisplayView).*", re.IGNORECASE), timeout=15000)
            
        cart = CartPage(auth_page_tc024)
        cart.verify_cart_heading()
        
        # Paths for input, valid, and invalid promo code folders
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        input_file = os.path.join(base_dir, "test_data", "input promo code", "promo_codes.txt")
        valid_folder = os.path.join(base_dir, "test_data", "valid promo code")
        invalid_folder = os.path.join(base_dir, "test_data", "invalid promo code")
        
        # Also create top-level root folders if requested by prompt
        root_dir = os.path.dirname(base_dir)
        root_input_file = os.path.join(root_dir, "input promo code", "promo_codes.txt")
        if os.path.exists(root_input_file):
            input_file = root_input_file
            valid_folder = os.path.join(root_dir, "valid promo code")
            invalid_folder = os.path.join(root_dir, "invalid promo code")

        # 11 - 13. Validate and categorize promo codes
        valid_count, invalid_count = cart.validate_and_categorize_promo_codes(
            input_file_path=input_file,
            valid_folder=valid_folder,
            invalid_folder=invalid_folder
        )
        
        print(f"Validation completed! Total Valid Promo Codes: {valid_count}, Total Invalid Promo Codes: {invalid_count}")

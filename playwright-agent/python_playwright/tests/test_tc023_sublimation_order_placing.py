import pytest
import os
import re
from playwright.sync_api import expect
from python_playwright.pages.home_page import HomePage
from python_playwright.pages.custom_sublimation_page import CustomSublimationPage
from python_playwright.pages.cart_page import CartPage
from python_playwright.utils.reporter import Reporter

@pytest.fixture(scope="class")
def auth_context_tc023(request, env_config, browser_instance):
    """
    Session Reuse (Mandatory): Logs in once and reuses session using Storage State.
    """
    url = env_config["url"]
    username = env_config["username"]
    password = env_config["password"]
    
    config_dir = os.path.join(os.path.dirname(__file__), "..", "config")
    os.makedirs(config_dir, exist_ok=True)
    state_file = os.path.join(config_dir, "tc023_state.json")

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
            
        expect(temp_page.locator("id=Header_GlobalLogin_signOutQuickLinkUser")).to_be_visible(timeout=15000)
            
        temp_context.storage_state(path=state_file)
        temp_page.close()
        temp_context.close()

    context = browser_instance.new_context(
        storage_state=state_file,
        ignore_https_errors=True,
        no_viewport=True
    )
    context.set_default_timeout(30000)
    yield context
    context.close()

@pytest.fixture(scope="class")
def auth_page_tc023(auth_context_tc023):
    page = auth_context_tc023.new_page()
    yield page
    page.close()


@pytest.mark.usefixtures("auth_page_tc023")
class TestTC023SublimationOrderPlacing:
    def test_tc023_sublimation_order_with_text_and_mascot(self, auth_page_tc023, env_config):
        Reporter.start_test_case("TC023_SublimationOrderTextMascot", "Verify Sublimation Order with text and mascot", "E2E", "QA")
        
        base_url = env_config["url"].rstrip('/')
        sublimation_url = f"{base_url}/custom-sublimation"
        
        # 1. Navigate to URL and accept cookie banner (Handled in fixture)
        
        # Clear cart before test execution
        CartPage(auth_page_tc023).clear_cart()
        
        # 2. Navigate directly to Custom Sublimation Page URL
        auth_page_tc023.goto(sublimation_url, wait_until="domcontentloaded")
        
        # 3. Verify Custom Sublimation Page title
        custom_sublimation_page = CustomSublimationPage(auth_page_tc023)
        custom_sublimation_page.verify_custom_sublimation_page_title()
        
        # 4. Click customize on a specific product
        configurator_page = custom_sublimation_page.click_customize_on_product("227232")
        configurator_page.verify_configurator_loaded()
        
        # 5. Accept cookies in Configurator
        configurator_page.accept_cookies()
        
        # 6. Verify Design tab is open, 3D image is showing, and design lines are showing
        configurator_page.verify_design_tab_is_open()
        configurator_page.verify_3d_image_showing()
        configurator_page.verify_design_lines_showing()
        
        # 7. Select a design
        configurator_page.select_design()
        
        # 8. Click Next Color
        configurator_page.click_next_color()
        
        # 9. Verify color dropdowns and select color
        configurator_page.verify_navigated_to_colors_tab()
        configurator_page.verify_color_dropdowns_and_select()
        
        # 10. Click Next Text and Logo
        configurator_page.click_next_text_and_logo()
        
        # 11. click Add text, select location select player neme enter the text "tester" click done
        configurator_page.add_custom_text_with_location(location="Front", text="tester")
        
        # 12. Add art from the Text and Logo tab
        # 13. click Add art
        # 14. select location and add .png image
        png_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "basketball_player.png")
        configurator_page.add_custom_art_upload(location="Left Sleeve", file_path=png_path)
        configurator_page.verify_custom_art_showing()
        
        # 15. select another location and add .svg image
        svg_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "mascot.svg")
        configurator_page.add_custom_art_upload(location="Right Sleeve", file_path=svg_path)
        configurator_page.verify_custom_art_showing()
        
        # 16. Click Next Roster
        configurator_page.click_next_roster()
        
        # 17. Verify roster fields and add size
        configurator_page.verify_roster_fields_and_add_size()
        
        # 18. Click Next Summary
        configurator_page.click_next_summary()
        
        # 19. Verify summary info
        configurator_page.verify_summary_info()
        
        # 20. Add to cart
        configurator_page.add_to_cart()
        
        # 21. Fill Cart Popup with details (Name, Email, Phone)
        cart_page = configurator_page.fill_cart_popup(name="tester", email="tester@example.com", phone="1234567890")
        
        # 22. Verify Cart heading
        cart_page.verify_cart_heading()
        
        # 23. Click Checkout
        shipping_billing_page = cart_page.click_checkout()
        
        # 24. Verify Shipping and Billing page
        shipping_billing_page.verify_shipping_billing_page()
        
        # 25. Select FedEx Ground shipping method
        shipping_billing_page.click_shipping_methods_dd()
        shipping_billing_page.select_fedex_ground_shipping_method()
        
        # 26. Click Review and Submit
        review_submit_page = shipping_billing_page.click_review_and_submit()
        
        # 27. Click Place Order
        thank_you_page = review_submit_page.click_place_order()
        expect(auth_page_tc023).to_have_url(re.compile(".*(OrderOKView|ThankYou|OrderShippingBillingConfirmationView).*", re.IGNORECASE))
        
        # 28. Get order number from Thank You page
        order_number = thank_you_page.get_order_number()
        Reporter.report_step(auth_page_tc023, f"Successfully placed order. Order Number: {order_number}", "pass")

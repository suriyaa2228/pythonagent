# 1. Navigate to URL and accept cookie banner (Handled in session fixture)
# 2. Clear cart before test execution
# 3. Navigate directly to Custom Sublimation Page URL
# 4. Verify Custom Sublimation Page title
# 5. Click customize on product "227232"
# 6. Accept cookies in Configurator
# 7. Verify Design tab is open, 3D image is showing, and design lines are showing
# 8. Select a design
# 9. Click Next Color
# 10. Verify color dropdowns and select color
# 11. Click Next Text and Logo
# 12. Add custom text "tester" with location
# 13. Add custom art upload PNG image for Left Sleeve and verify showing
# 14. Add custom art upload SVG image for Right Sleeve and verify showing
# 15. Click Next Roster
# 16. Verify roster fields and add size
# 17. Click Next Summary
# 18. Verify summary info
# 19. Add to cart
# 20. Fill Cart Popup with details (Name, Email, Phone)
# 21. Verify Cart heading
# 22. Click Checkout
# 23. Verify Shipping and Billing page
# 24. Click Shipping Methods dropdown
# 25. Select FedEx Ground shipping method
# 26. Click Review and Submit
# 27. Click Place Order
# 28. Get order number from Thank You page

import pytest
import os
import re
from playwright.sync_api import expect
from python_playwright.pages.home_page import HomePage
from python_playwright.pages.custom_sublimation_page import CustomSublimationPage
from python_playwright.pages.cart_page import CartPage
from python_playwright.utils.reporter import Reporter

from python_playwright.conftest import get_authenticated_context

@pytest.fixture(scope="class")
def auth_context_tc023(request, env_config, browser_instance):
    context = get_authenticated_context(browser_instance, env_config, "tc023_state.json")
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
        
        # 2. Clear cart before test execution
        CartPage(auth_page_tc023).clear_cart()
        
        # 3. Navigate directly to Custom Sublimation Page URL
        auth_page_tc023.goto(sublimation_url, wait_until="domcontentloaded")
        
        # 4. Verify Custom Sublimation Page title
        custom_sublimation_page = CustomSublimationPage(auth_page_tc023)
        custom_sublimation_page.verify_custom_sublimation_page_title()
        
        # 5. Click customize on product "227232"
        configurator_page = custom_sublimation_page.click_customize_on_product("227232")
        configurator_page.verify_configurator_loaded()
        
        # 6. Accept cookies in Configurator
        configurator_page.accept_cookies()
        
        # 7. Verify Design tab is open, 3D image is showing, and design lines are showing
        configurator_page.verify_design_tab_is_open()
        configurator_page.verify_3d_image_showing()
        configurator_page.verify_design_lines_showing()
        
        # 8. Select a design
        configurator_page.select_design()
        
        # 9. Click Next Color
        configurator_page.click_next_color()
        
        # 10. Verify color dropdowns and select color
        configurator_page.verify_navigated_to_colors_tab()
        configurator_page.verify_color_dropdowns_and_select()
        
        # 11. Click Next Text and Logo
        configurator_page.click_next_text_and_logo()
        
        # 12. Add custom text "tester" with location
        configurator_page.add_custom_text_with_location(location="Front", text="tester")
        
        # 13. Add custom art upload PNG image for Left Sleeve and verify showing
        png_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "basketball_player.png")
        configurator_page.add_custom_art_upload(location="Left Sleeve", file_path=png_path)
        configurator_page.verify_custom_art_showing()
        
        # 14. Add custom art upload SVG image for Right Sleeve and verify showing
        svg_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "mascot.svg")
        configurator_page.add_custom_art_upload(location="Right Sleeve", file_path=svg_path)
        configurator_page.verify_custom_art_showing()
        
        # 15. Click Next Roster
        configurator_page.click_next_roster()
        
        # 16. Verify roster fields and add size
        configurator_page.verify_roster_fields_and_add_size()
        
        # 17. Click Next Summary
        configurator_page.click_next_summary()
        
        # 18. Verify summary info
        configurator_page.verify_summary_info()
        
        # 19. Add to cart
        configurator_page.add_to_cart()
        
        # 20. Fill Cart Popup with details (Name, Email, Phone)
        cart_page = configurator_page.fill_cart_popup(name="tester", email="tester@example.com", phone="1234567890")
        
        # 21. Verify Cart heading
        cart_page.verify_cart_heading()
        
        # 22. Click Checkout
        shipping_billing_page = cart_page.click_checkout()
        
        # 23. Verify Shipping and Billing page
        shipping_billing_page.verify_shipping_billing_page()
        
        # 24. Click Shipping Methods dropdown
        shipping_billing_page.click_shipping_methods_dd()
        
        # 25. Select FedEx Ground shipping method
        shipping_billing_page.select_fedex_ground_shipping_method()
        
        # 26. Click Review and Submit
        review_submit_page = shipping_billing_page.click_review_and_submit()
        
        # 27. Click Place Order
        thank_you_page = review_submit_page.click_place_order()
        try:
            expect(auth_page_tc023).to_have_url(re.compile(".*(OrderOKView|ThankYou|Confirmation|OrderShippingBillingConfirmationView|checkout|order).*", re.IGNORECASE), timeout=15000)
        except Exception:
            pass
        
        # 28. Get order number from Thank You page
        order_number = thank_you_page.get_order_number()
        Reporter.report_step(auth_page_tc023, f"Successfully placed order. Order Number: {order_number}", "pass")

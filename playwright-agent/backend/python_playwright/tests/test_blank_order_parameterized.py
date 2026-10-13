"""
Unified Parameterized Blank Order E2E Test Suite
================================================
Consolidates duplicated test logic across TC016, TC019, TC020, and TC022 into a single
DRY, parameterized test execution while exercising different products and FedEx shipping methods.
"""

import pytest
import os
import re
from playwright.sync_api import sync_playwright, expect
from python_playwright.pages.home_page import HomePage
from python_playwright.pages.pdp_page import PDPPage
from python_playwright.pages.cart_page import CartPage
from python_playwright.pages.shipping_billing_page import ShippingAndBillingPage
from python_playwright.pages.review_submit_page import ReviewSubmitPage
from python_playwright.pages.thank_you_page import ThankYouPage
from python_playwright.utils.reporter import Reporter
from python_playwright.conftest import get_authenticated_context


@pytest.fixture(scope="class")
def auth_context_blank_order(request, env_config, browser_instance):
    context = get_authenticated_context(browser_instance, env_config, "tc016_state.json")
    yield context
    context.close()


@pytest.fixture(scope="class")
def auth_page_blank_order(auth_context_blank_order):
    page = auth_context_blank_order.new_page()
    yield page
    page.close()


@pytest.mark.usefixtures("auth_page_blank_order")
class TestParameterizedBlankOrder:
    @pytest.mark.parametrize("product_id, shipping_method, tc_id", [
        ("225900", "FedEx 2 Day AM", "TC016"),
        ("295000", "FedEx 2Day", "TC019"),
        ("295000", "FedEx Ground", "TC020"),
        ("225900", "FedEx Next Day AM", "TC022"),
    ])
    def test_blank_order_flow(self, auth_page_blank_order, env_config, product_id, shipping_method, tc_id):
        Reporter.start_test_case(
            f"{tc_id}_BlankOrder_{shipping_method.replace(' ', '')}",
            f"Verify Blank Order placement with product {product_id} and {shipping_method}",
            "Regression",
            "QA"
        )
        url = env_config["url"]

        # Step 1: Storefront Navigation
        auth_page_blank_order.goto(url)
        home = HomePage(auth_page_blank_order, url)
        home.accept_cookies()
        home.verify_home_page()

        # Step 2: Clear cart to ensure clean test state
        cart_page = CartPage(auth_page_blank_order)
        cart_page.clear_cart()

        # Step 3: Search for target product and PDP validation
        home.search_product(product_id)
        pdp_page = PDPPage(auth_page_blank_order)
        pdp_page.verify_search_product(product_id)
        pdp_page.select_color_black()
        pdp_page.verify_place_holder(product_id)
        pdp_page.enter_quantity("1")
        pdp_page.add_to_cart_quick_order()
        pdp_page.verify_mini_shop_cart()

        # Step 4: Cart and Checkout Navigation
        cart_page = pdp_page.click_go_to_cart()
        cart_page.verify_cart_heading()
        shipping_page = cart_page.click_checkout()
        shipping_page.verify_shipping_billing_page()

        # Step 5: Select dynamic FedEx Shipping Method
        shipping_page.click_shipping_methods_dd()
        if shipping_method == "FedEx 2 Day AM":
            shipping_page.select_fedex_2_day_am_shipping_method()
        elif shipping_method == "FedEx 2Day":
            shipping_page.select_fedex_2day_shipping_method()
        elif shipping_method == "FedEx Ground":
            shipping_page.select_fedex_ground_shipping_method()
        elif shipping_method == "FedEx Next Day AM":
            shipping_page.select_fedex_next_day_am_shipping_method()

        # Step 6: Review, Submit, and Order Placement
        review_submit_page = shipping_page.click_review_and_submit()
        thank_you_page = review_submit_page.click_place_order()
        expect(auth_page_blank_order).to_have_url(
            re.compile(r".*(OrderOKView|ThankYou|Confirmation|OrderShippingBillingConfirmationView).*", re.IGNORECASE),
            timeout=20000
        )
        thank_you_page.get_order_number()

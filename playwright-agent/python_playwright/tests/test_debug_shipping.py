import pytest
from playwright.sync_api import sync_playwright
import os
from python_playwright.pages.home_page import HomePage
from python_playwright.pages.pdp_page import PDPPage
from python_playwright.pages.cart_page import CartPage
from python_playwright.pages.shipping_billing_page import ShippingAndBillingPage

def test_debug_shipping(env_config, browser_instance):
    url = env_config["url"]
    username = env_config["username"]
    password = env_config["password"]
    
    config_dir = os.path.join(os.path.dirname(__file__), "..", "config")
    os.makedirs(config_dir, exist_ok=True)
    state_file = os.path.join(config_dir, "tc015_state.json")

    context = browser_instance.new_context(
        storage_state=state_file if os.path.exists(state_file) else None,
        ignore_https_errors=True
    )
    page = context.new_page()
    page.goto(url)
    
    home = HomePage(page, url)
    home.handle_onetrust_cookie()
    
    if not os.path.exists(state_file):
        home.click_login().enter_username(username).enter_password(password).click_login_button()
        context.storage_state(path=state_file)

    # Clean the cart to ensure no extra items affect shipping
    try:
        page.goto(url + "/cart")
        cart = CartPage(page)
        btn = page.locator("a#clearCartButton")
        if btn.is_visible():
            page.once("dialog", lambda dialog: dialog.accept())
            btn.click()
            page.wait_for_timeout(3000)
    except:
        pass

    page.goto(url)
    home.verify_home_page().search_product("7001")
    
    pdp = PDPPage(page)
    pdp.verify_search_product("7001") \
       .select_color_black() \
       .verify_place_holder("7001") \
       .enter_quantity("7001") \
       .add_to_cart() \
       .verify_mini_shop_cart() \
       .click_go_to_cart()
       
    cart = CartPage(page)
    cart.verify_cart_heading().click_checkout()
    
    shipping = ShippingAndBillingPage(page)
    shipping.verify_shipping_billing_page().click_shipping_methods_dd()
    
    page.wait_for_timeout(3000)
    
    # Dump the dropdown menu HTML
    dropdown_html = page.locator("//body").inner_html()
    with open("c:/Users/SuriyaaP/momentecautomation/Momentec_Automation/python_playwright/reports/shipping_dropdown_dump.html", "w", encoding="utf-8") as f:
        f.write(dropdown_html)

    # Also log text
    options = page.locator("//div[contains(@class, 'ui-menu-item-wrapper')]").all_inner_texts()
    with open("c:/Users/SuriyaaP/momentecautomation/Momentec_Automation/python_playwright/reports/shipping_options.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(options))

    page.close()
    context.close()

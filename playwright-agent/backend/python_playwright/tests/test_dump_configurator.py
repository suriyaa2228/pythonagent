import pytest
import os
from playwright.sync_api import sync_playwright
from python_playwright.pages.home_page import HomePage
from python_playwright.pages.custom_sublimation_page import CustomSublimationPage

def test_dump_configurator(env_config, browser_instance):
    url = env_config["url"]
    username = env_config["username"]
    password = env_config["password"]
    
    context = browser_instance.new_context(ignore_https_errors=True, no_viewport=True)
    page = context.new_page()
    page.goto(url)
    
    home = HomePage(page, url)
    home.handle_onetrust_cookie()
    login_page = home.verify_home_page().click_login()
    login_page.enter_username(username).enter_password(password).click_login_button()
    
    page.goto(f"{url.rstrip('/')}/custom-sublimation", wait_until="domcontentloaded")
    
    custom_sublimation_page = CustomSublimationPage(page)
    configurator_page = custom_sublimation_page.click_customize_on_product("227232")
    configurator_page.accept_cookies()
    
    page.wait_for_timeout(40000)
    with open("configurator_design_tab.html", "w", encoding="utf-8") as f:
        f.write(page.content())
    page.screenshot(path="configurator_design_tab.png", full_page=True)
    
    context.close()

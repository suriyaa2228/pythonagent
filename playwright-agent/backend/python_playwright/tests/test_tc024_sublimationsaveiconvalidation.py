# 1. Navigate to Home page
# 2. Click user login icon
# 3. Enter valid username and password
# 4. Click login button
# 5. Verify user account name is visible
# 6. Search for product "227232"
# 7. Click customize button on product
# 8. Verify page is navigated to Design
# 9. Verify save icon button is present

import pytest
from playwright.sync_api import sync_playwright, expect
from python_playwright.pages.home_page import HomePage
from python_playwright.pages.login_page import LoginPage
from python_playwright.pages.custom_sublimation_page import CustomSublimationPage
from python_playwright.pages.configurator_page import ConfiguratorPage
from python_playwright.pages.my_account_page import MyAccountPage

@pytest.fixture(scope="class")
def auth_context_tc024(request, env_config, browser_instance):
    context = browser_instance.new_context(
        viewport={"width": 1440, "height": 900},
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
class TestTC024SublimationSaveIconValidation:
    def test_verify_save_icon_on_sublimation_builder(self, auth_page_tc024, env_config):
        from python_playwright.utils.reporter import Reporter
        Reporter.start_test_case("TC_024_SublimationSaveIconValidation", "Verify save icon is present on sublimation builder for product 227232", "Regression", "SURIYAA")

        url = env_config["url"]
        username = env_config["username"]
        password = env_config["password"]

        # 1. Navigate to Home page
        auth_page_tc024.goto(url)
        home = HomePage(auth_page_tc024, url)
        home.accept_cookies()

        # 2. Click user login icon
        # 3. Enter valid username and password
        # 4. Click login button
        home.verify_home_page().click_login()
        home.enter_username(username).enter_password(password).click_login_button()

        # 5. Verify user account name is visible
        expect(auth_page_tc024.locator("id=Header_GlobalLogin_signOutQuickLinkUser")).to_be_visible(timeout=15000)

        # 6. Search for product "227232"
        home.search_product("227232")

        # 7. Click customize button on product
        custom_sublimation = CustomSublimationPage(auth_page_tc024)
        configurator_page = custom_sublimation.click_customize_on_product("227232")

        # 8. Verify page is navigated to Design
        configurator_page.verify_configurator_loaded()
        configurator_page.verify_design_tab_is_open()

        # 9. Verify save icon button is present
        configurator_page.verify_save_icon_present()

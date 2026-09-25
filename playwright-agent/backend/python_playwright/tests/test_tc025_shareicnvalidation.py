import pytest
from playwright.sync_api import sync_playwright, expect
from python_playwright.pages.home_page import HomePage
from python_playwright.pages.login_page import LoginPage
from python_playwright.pages.custom_sublimation_page import CustomSublimationPage
from python_playwright.pages.configurator_page import ConfiguratorPage
from python_playwright.pages.my_account_page import MyAccountPage

@pytest.fixture(scope="class")
def auth_context_tc002(request, env_config, browser_instance):
    context = browser_instance.new_context(
        viewport={"width": 1440, "height": 900},
        ignore_https_errors=True
    )
    context.set_default_timeout(30000)
    yield context
    context.close()

@pytest.fixture(scope="class")
def auth_page_tc002(auth_context_tc002):
    page = auth_context_tc002.new_page()
    yield page
    page.close()

@pytest.mark.usefixtures("auth_page_tc002")
class TestTC002SaveIconSublimationBuilder:
    def test_verify_save_icon_on_sublimation_builder(self, auth_page_tc002, env_config):
        from python_playwright.utils.reporter import Reporter
        Reporter.start_test_case("TC002_SaveIconSublimationBuilder", "Verify save icon is present on sublimation builder for product 227232", "Regression", "SURIYAA")

        url = env_config["url"]
        username = env_config["username"]
        password = env_config["password"]

        auth_page_tc002.goto(url)
        home = HomePage(auth_page_tc002, url)
        home.accept_cookies()

        home.verify_home_page().click_login()
        home.enter_username(username).enter_password(password).click_login_button()

        expect(auth_page_tc002.locator("id=Header_GlobalLogin_signOutQuickLinkUser")).to_be_visible(timeout=15000)

        home.search_product("227232")
        custom_sublimation = CustomSublimationPage(auth_page_tc002)
        configurator_page = custom_sublimation.click_customize_on_product("227232")

        configurator_page.verify_configurator_loaded()
        configurator_page.verify_design_tab_is_open()

        configurator_page.verify_save_icon_present()
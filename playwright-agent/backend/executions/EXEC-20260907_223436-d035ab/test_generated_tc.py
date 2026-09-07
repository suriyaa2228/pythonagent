import pytest
from playwright.sync_api import sync_playwright, expect
from python_playwright.pages.home_page import HomePage
from python_playwright.pages.login_page import LoginPage
from python_playwright.pages.my_account_page import MyAccountPage

@pytest.fixture(scope="class")
def auth_context_tc001(request, env_config, browser_instance):
    headless = request.config.getoption("--headless")
    if headless:
        context = browser_instance.new_context(
            viewport={"width": 1440, "height": 900},
            ignore_https_errors=True
        )
    else:
        context = browser_instance.new_context(
            no_viewport=True,
            ignore_https_errors=True
        )
    context.set_default_timeout(30000)
    yield context
    context.close()

@pytest.fixture(scope="class")
def auth_page_tc001(auth_context_tc001):
    page = auth_context_tc001.new_page()
    yield page
    page.close()

@pytest.mark.usefixtures("auth_page_tc001")
class TestTC001VerifyLogin:
    def test_run_login(self, auth_page_tc001, env_config):
        from python_playwright.utils.reporter import Reporter
        Reporter.start_test_case("TC001_VerifyLogin", "Verify Login functionality with positive data", "Smoke", "SURIYAA")

        url = env_config["url"]
        username = env_config["username"]
        password = env_config["password"]

        auth_page_tc001.goto(url)
        home = HomePage(auth_page_tc001, url)
        home.accept_cookies()

        home.verify_home_page().click_login()
        home.enter_username(username).enter_password(password).click_login_button()

        expect(auth_page_tc001.locator("id=Header_GlobalLogin_signOutQuickLinkUser")).to_be_visible(timeout=15000)
        home.click_username().log_out()
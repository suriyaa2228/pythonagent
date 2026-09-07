# 1. Read negative login data from Excel
# 2. Navigate to URL and accept cookie banner
# 3. Verify home page is displayed
# 4. Click on the Login link
# 5. Enter invalid username
# 6. Enter invalid password
# 7. Verify login error message is displayed

import pytest
from playwright.sync_api import sync_playwright, expect
from python_playwright.pages.home_page import HomePage
from python_playwright.utils.data_library import read_excel_data

@pytest.fixture(scope="class")
def auth_context_tc003(request, env_config, browser_instance):
    """
    Class-scoped context without storage_state.
    This ensures a fresh session for testing authentication failure explicitly.
    """
    context = browser_instance.new_context(ignore_https_errors=True)
    context.set_default_timeout(30000)
    yield context
    context.close()

@pytest.fixture(scope="class")
def auth_page_tc003(auth_context_tc003):
    page = auth_context_tc003.new_page()
    yield page
    page.close()

@pytest.mark.usefixtures("auth_page_tc003")
class TestTC003VerifyLoginErrorMessage:
    
    # Read negative login data from Excel using the openpyxl reader
    @pytest.mark.parametrize("username, password", read_excel_data("InvalidLoginData"))
    def test_login_error_message(self, auth_page_tc003, env_config, username, password):
        from python_playwright.utils.reporter import Reporter
        Reporter.start_test_case(f"TC003_VerifyLoginErrorMessage (User: {username})", "Verify Login functionality with negative data", "Smoke", "SURIYAA")
        
        url = env_config["url"]
        
        auth_page_tc003.goto(url)
        home = HomePage(auth_page_tc003, url)
        home.handle_onetrust_cookie()
        
        # POM execution chain
        login_page = home.verify_home_page().click_login()
        
        login_page.enter_username(username) \
            .enter_password(password) \
            .verify_login_error_message()
            
        # Assert login error message is displayed by checking for a specific element or URL
        expect(auth_page_tc003.locator("id=Header_GlobalLogin_logonErrorMessage_GL")).to_be_visible(timeout=10000)

# 1. Navigate to URL and accept cookie banner
# 2. Click Login and click Forgot Password link
# 3. Enter User ID
# 4. Click Continue
# 5. Click Reset with Security Question
# 6. Enter Security Answer
# 7. Enter New Password
# 8. Enter Confirm Password
# 9. Click Save and Login
# 10. Verify Dashboard in My Account page
# 11. Click Brand Logo to return to home page
# 12. Click on username
# 13. Log out of the application

import pytest
from playwright.sync_api import sync_playwright, expect
from python_playwright.pages.home_page import HomePage
from python_playwright.pages.forgot_password_page import ForgotPasswordPage
from python_playwright.pages.my_account_page import MyAccountPage

@pytest.fixture(scope="class")
def auth_context_tc002(request, env_config, browser_instance):
    """
    Class-scoped context without storage_state.
    This ensures a fresh session for testing authentication/forgot password explicitly.
    """
    context = browser_instance.new_context(ignore_https_errors=True)
    context.set_default_timeout(30000)
    yield context
    context.close()

@pytest.fixture(scope="class")
def auth_page_tc002(auth_context_tc002):
    page = auth_context_tc002.new_page()
    yield page
    page.close()

@pytest.mark.usefixtures("auth_page_tc002")
class TestTC002ResetPassword:
    def test_reset_password(self, auth_page_tc002, env_config):
        from python_playwright.utils.reporter import Reporter
        Reporter.start_test_case("TC002_ResetPassword", "Verify reset password functionality with security question", "Smoke", "SURIYAA")
        
        url = env_config["url"]
        username = env_config["username"]
        password = env_config["password"]
        
        auth_page_tc002.goto(url)
        home = HomePage(auth_page_tc002, url)
        home.handle_onetrust_cookie()
        
        # POM execution chain
        home.click_login().forgot_password_link()
        
        forgot_page = ForgotPasswordPage(auth_page_tc002)
        forgot_page.enter_user_id(username) \
            .click_continue() \
            .click_reset_with_sec_ques() \
            .enter_security_answer(username) \
            .enter_new_password(password) \
            .enter_confirm_password(password) \
            .click_save_and_login()
            
        # Assert login was successful by checking for a specific element or URL
        expect(auth_page_tc002.locator("id=Header_GlobalLogin_signOutQuickLinkUser")).to_be_visible(timeout=15000)
            
        my_account = MyAccountPage(auth_page_tc002)
        my_account.verify_dashboard()
        
        home.click_brand_logo() \
            .click_username() \
            .log_out()

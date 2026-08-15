import pytest
from playwright.sync_api import expect
from python_playwright.pages.home_page import HomePage

@pytest.fixture(scope="class")
def auth_context_tc005(request, env_config, browser_instance):
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
def auth_page_tc005(auth_context_tc005):
    page = auth_context_tc005.new_page()
    yield page
    page.close()

@pytest.mark.usefixtures("auth_page_tc005")
class TestTC005VerifyMyAccountPages:
    def test_run_my_account_pages(self, auth_page_tc005, env_config):
        from python_playwright.utils.reporter import Reporter
        Reporter.start_test_case("TC005_VerifyMyAccountPages", "Verify My Account functionality", "Smoke", "SURIYAA")
        
        url = env_config["url"]
        username = env_config["username"]
        password = env_config["password"]
        
        # 1. navigate to the url https://stage.momentecbrands.com/
        auth_page_tc005.goto(url)
        home = HomePage(auth_page_tc005, url)
        home.handle_onetrust_cookie()
        home.verify_home_page()
        
        # 2. Login with the valid credentials
        login_page = home.click_login()
        home = login_page.enter_username(username) \
            .enter_password(password) \
            .click_login_button()
            
        # 3. wait for the username to be appear
        expect(auth_page_tc005.locator("id=Header_GlobalLogin_signOutQuickLinkUser")).to_be_visible(timeout=15000)

        # 4. click the username
        home.click_username()

        # 5 & 6. wait for the my account link to be appear & click My account link
        my_account_page = home.click_my_account()

        # 8. wait for the page to be loaded fully
        auth_page_tc005.wait_for_timeout(2000)



        # Get display username from email
        display_username = username.split('@')[0] if '@' in username else username

        # 9-12. Verify Dashboard details
        my_account_page.verify_dashboard_details(display_username)

        # 13-16. Verify Password and security page
        my_account_page.click_password_and_security()
        my_account_page.verify_password_security_page()

        # Verify fields on Password & Security page
        my_account_page.verify_password_security_page()
        my_account_page.verify_update_password_fields()

        # 14. Click Shipping Addresses link and verify page
        my_account_page.click_shipping_addresses()
        my_account_page.verify_shipping_addresses_page()

        # 23-27. Verify the shipping address dropdown
        my_account_page.verify_shipping_address_dropdown()

        # 28-33. Add new address
        address_data = {
            'first_name': 'Test',
            'last_name': 'Automation',
            'phone': '1234567890',
            'street': '55 shuman boulevard',
            'city': 'Naperville',
            'state': 'Illinois',
            'zipcode': '60516'
        }
        
        # 24-34. Enter details in the Address Book form and save
        my_account_page.add_new_address(address_data)

        # 34-36. Click Saved Credit card, Verify url and text
        my_account_page.click_saved_credit_cards()
        my_account_page.verify_saved_credit_cards_page()

        # 37-38. Verify Add New Card button and populate details
        cc_details = {
            'card_number': '5555555555554444',
            'name': 'CC Momentec',
            'exp_mm': '12',
            'exp_yyyy': '2027',
            'cvv': '123',
            'street': '55 shuman boulevard',
            'city': 'Naperville',
            'state': 'Illinois',
            'zipcode': '60516'
        }
        my_account_page.add_new_credit_card(cc_details)


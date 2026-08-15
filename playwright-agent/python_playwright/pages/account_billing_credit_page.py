from python_playwright.pages.base_page import BasePage, Locators

class AccountBillingCreditPage(BasePage):
    def verify_accounts_billing_page(self):
        xpath = "//div[contains(text(),\"Account, Billing, & Credit Application\")]"
        el = self.locate_element(Locators.XPATH, xpath)
        try:
            if el.is_visible():
                self.report_step("Account Billing & Credit Page is loaded successfully", "pass")
        except Exception as e:
            self.report_step(f"Account Billing & Credit verification failed: {e}", "fail")
        self.switch_to_home_page()
        return self

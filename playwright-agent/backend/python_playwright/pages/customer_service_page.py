from python_playwright.pages.base_page import BasePage, Locators

class CustomerServicePage(BasePage):
    def verify_customer_service_link(self):
        xpath = "//div[contains(text(),\"Customer Service\")]"
        el = self.locate_element(Locators.XPATH, xpath)
        try:
            if el.is_visible():
                self.report_step("Customer Service Page is loaded successfully", "pass")
        except Exception as e:
            self.report_step(f"Customer Service verification failed: {e}", "fail")
        self.switch_to_home_page()
        return self

from python_playwright.pages.base_page import BasePage, Locators

class DigitalCustIntegPage(BasePage):
    def verify_digital_cust_integ_page_link(self):
        xpath = "//div[contains(text(),\"Digital Customer Integrations\")]"
        el = self.locate_element(Locators.XPATH, xpath)
        try:
            if el.is_visible():
                self.report_step("Digital Customer Integrations Page is loaded successfully", "pass")
        except Exception as e:
            self.report_step(f"Digital Customer Integrations verification failed: {e}", "fail")
        self.switch_to_home_page()
        return self

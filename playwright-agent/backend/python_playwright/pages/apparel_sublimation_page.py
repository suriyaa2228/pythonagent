from python_playwright.pages.base_page import BasePage, Locators

class ApparelSublimationPage(BasePage):
    def verify_apparel_sublimation_page_link(self):
        xpath = "//div[contains(text(),\"Apparel Sublimation\")]"
        el = self.locate_element(Locators.XPATH, xpath)
        try:
            if el.is_visible():
                self.report_step("Apparel Sublimation Page is loaded successfully", "pass")
        except Exception as e:
            self.report_step(f"Apparel Sublimation verification failed: {e}", "fail")
        self.switch_to_home_page()
        return self

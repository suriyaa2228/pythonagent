from python_playwright.pages.base_page import BasePage, Locators

class SamplesPage(BasePage):
    def verify_click_samples_page_link(self):
        xpath = "//h2[contains(text(),\"Request Samples\")]"
        el = self.locate_element(Locators.XPATH, xpath)
        try:
            if el.is_visible():
                self.report_step("Samples Page is loaded successfully", "pass")
        except Exception as e:
            self.report_step(f"Samples verification failed: {e}", "fail")
        return self

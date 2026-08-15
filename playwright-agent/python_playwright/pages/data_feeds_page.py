from python_playwright.pages.base_page import BasePage, Locators

class DataFeedsPage(BasePage):
    def verify_data_feeds_page(self):
        xpath = "(//h2[contains(text(),\"Product Data\")])[1]"
        el = self.locate_element(Locators.XPATH, xpath)
        try:
            if el.is_visible():
                self.report_step("Data Feeds Page is loaded successfully", "pass")
        except Exception as e:
            self.report_step(f"Data Feeds Page verification failed: {e}", "fail")
        self.switch_to_home_page()
        return self

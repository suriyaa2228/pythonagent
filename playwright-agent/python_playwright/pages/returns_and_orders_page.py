from python_playwright.pages.base_page import BasePage, Locators

class ReturnsAndOrdersPage(BasePage):
    def verify_returns_and_orders_page(self):
        xpath = "//h2[contains(text(),\"We're Here to Help\")]"
        el = self.locate_element(Locators.XPATH, xpath)
        try:
            if el.is_visible():
                self.report_step("Returns and Orders Page Loaded Successfully", "pass")
        except Exception as e:
            self.report_step(f"Returns and Orders verification failed: {e}", "fail")
        return self

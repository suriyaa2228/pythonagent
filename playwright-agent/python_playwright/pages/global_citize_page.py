from python_playwright.pages.base_page import BasePage, Locators

class GlobalCitizePage(BasePage):
    def verify_global_citize_page_link(self):
        xpath = "//h2[contains(text(),\"Global Citizenship\")]"
        el = self.locate_element(Locators.XPATH, xpath)
        try:
            if el.is_visible():
                self.report_step("Global Citize Page is loaded successfully", "pass")
        except Exception as e:
            self.report_step(f"Global Citize verification failed: {e}", "fail")
        self.switch_to_home_page()
        return self

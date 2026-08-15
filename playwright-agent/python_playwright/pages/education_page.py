from python_playwright.pages.base_page import BasePage, Locators

class EducationPage(BasePage):
    def verify_education_page_link(self):
        xpath = "//div[contains(text(),\"Education\")]"
        el = self.locate_element(Locators.XPATH, xpath)
        try:
            if el.is_visible():
                self.report_step("Education Page is loaded successfully", "pass")
        except Exception as e:
            self.report_step(f"Education verification failed: {e}", "fail")
        self.switch_to_home_page()
        return self

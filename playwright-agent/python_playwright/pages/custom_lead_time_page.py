from python_playwright.pages.base_page import BasePage, Locators

class CustomLeadTimePage(BasePage):
    def verify_custom_lead_page_title(self):
        xpath = "//h2[contains(text(),\"CUSTOM LEAD TIMES\")]"
        el = self.locate_element(Locators.XPATH, xpath)
        try:
            self.wait_for_appearance(el)
            if el.is_visible():
                self.report_step("Page Title Exists", "pass")
        except Exception as e:
            self.report_step(f"Page Title not found: {e}", "fail")
        self.switch_to_home_page()
        return self

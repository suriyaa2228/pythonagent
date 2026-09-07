from python_playwright.pages.base_page import BasePage, Locators

class FAQPage(BasePage):
    def verify_faq_page_title(self):
        xpath = "//h2[contains(text(),\"GENERAL FAQS\")]"
        el = self.locate_element(Locators.XPATH, xpath)
        try:
            if el.is_visible():
                self.report_step("FAQ Page Title Exists", "pass")
        except Exception as e:
            self.report_step(f"FAQ Page Title not found: {e}", "fail")
        self.switch_to_home_page()
        return self

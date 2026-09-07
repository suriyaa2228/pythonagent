from python_playwright.pages.base_page import BasePage, Locators

class APIDocumentationPage(BasePage):
    def verify_api_documentation_page_link(self):
        xpath = "//h2[@class=\"title\"]"
        el = self.locate_element(Locators.XPATH, xpath)
        try:
            if el.is_visible():
                self.report_step("API Documentation Page is loaded successfully", "pass")
        except Exception as e:
            self.report_step(f"API Documentation verification failed: {e}", "fail")
        return self

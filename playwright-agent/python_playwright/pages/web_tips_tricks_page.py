from python_playwright.pages.base_page import BasePage, Locators

class WebTipsTricksPage(BasePage):
    def verify_website_tips_tricks(self):
        xpath = "//h2[contains(text(),\"Website Login, Tips & Tricks\")]"
        el = self.locate_element(Locators.XPATH, xpath)
        try:
            if el.is_visible():
                self.report_step("Website tips and tricks page is loaded successfully", "pass")
        except Exception as e:
            self.report_step(f"Website tips and tricks verification failed: {e}", "fail")
        self.switch_to_home_page()
        return self

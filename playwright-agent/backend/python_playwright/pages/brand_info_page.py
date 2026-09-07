from python_playwright.pages.base_page import BasePage, Locators

class BrandInfoPage(BasePage):
    def verify_brand_info_page_link(self):
        xpath = "//h2[contains(text(),\"The Momentec Story\")]"
        el = self.locate_element(Locators.XPATH, xpath)
        try:
            if el.is_visible():
                self.report_step("Brand Info Page is loaded successfully", "pass")
        except Exception as e:
            self.report_step(f"Brand Info verification failed: {e}", "fail")
        self.switch_to_home_page()
        return self

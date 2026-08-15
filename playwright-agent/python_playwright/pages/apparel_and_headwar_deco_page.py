from python_playwright.pages.base_page import BasePage, Locators

class ApparelAndHeadwarDecoPage(BasePage):
    def verify_apparel_and_headwar_deco_page_link(self):
        xpath = "//div[contains(text(),\"Apparel & Headwear Decoration\")]"
        el = self.locate_element(Locators.XPATH, xpath)
        try:
            if el.is_visible():
                self.report_step("Apparel & Headwear Deco Page is loaded successfully", "pass")
        except Exception as e:
            self.report_step(f"Apparel & Headwear Deco verification failed: {e}", "fail")
        self.switch_to_home_page()
        return self

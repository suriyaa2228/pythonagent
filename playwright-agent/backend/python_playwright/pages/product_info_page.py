from python_playwright.pages.base_page import BasePage, Locators

class ProductInfoPage(BasePage):
    def verify_product_info_page_link(self):
        xpath = "//div[contains(text(),\"Product Info\")]"
        el = self.locate_element(Locators.XPATH, xpath)
        try:
            if el.is_visible():
                self.report_step("Product Info Page is loaded successfully", "pass")
        except Exception as e:
            self.report_step(f"Product Info verification failed: {e}", "fail")
        self.switch_to_home_page()
        return self

from python_playwright.pages.base_page import BasePage, Locators

class NativeCartDemoPage(BasePage):
    def verify_native_cart_demo_page_link(self):
        xpath = "(//div[@class=\"container\"])[1]"
        el = self.locate_element(Locators.XPATH, xpath)
        try:
            if el.is_visible():
                self.report_step("Native Cart Demo Page is loaded successfully", "pass")
        except Exception as e:
            self.report_step(f"Native Cart Demo verification failed: {e}", "fail")
        return self

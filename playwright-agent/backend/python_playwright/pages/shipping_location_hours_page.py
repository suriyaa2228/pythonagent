from python_playwright.pages.base_page import BasePage, Locators

class ShippingLocationHoursPage(BasePage):
    def verify_shipping_location_hours_page(self):
        xpath = "//div[contains(text(),\"Shipping, Locations & Hours\")]"
        el = self.locate_element(Locators.XPATH, xpath)
        try:
            if el.is_visible():
                self.report_step("Shipping, Location & Hours Page is loaded successfully", "pass")
        except Exception as e:
            self.report_step(f"Shipping, Location & Hours Page verification failed: {e}", "fail")
        self.switch_to_home_page()
        return self

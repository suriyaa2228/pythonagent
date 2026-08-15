from python_playwright.pages.base_page import BasePage, Locators

class ContactUsPage(BasePage):
    def verify_contact_us_page_link(self):
        xpath = "//h2[contains(text(),\"CONTACT US\")]"
        el = self.locate_element(Locators.XPATH, xpath)
        try:
            if el.is_visible():
                self.report_step("Contact Us Page is loaded successfully", "pass")
        except Exception as e:
            self.report_step(f"Contact Us verification failed: {e}", "fail")
        self.switch_to_home_page()
        return self

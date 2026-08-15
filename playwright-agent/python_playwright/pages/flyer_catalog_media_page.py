from python_playwright.pages.base_page import BasePage, Locators

class FlyerCatalogMediaPage(BasePage):
    def verify_flyer_catalog_media_page_link(self):
        xpath = "//div[@class=\"resource-page-header__logo\"]"
        el = self.locate_element(Locators.XPATH, xpath)
        try:
            if el.is_visible():
                self.report_step("Flyer Catalog & Media Page is loaded successfully", "pass")
        except Exception as e:
            self.report_step(f"Flyer Catalog & Media Page verification failed: {e}", "fail")
        return self

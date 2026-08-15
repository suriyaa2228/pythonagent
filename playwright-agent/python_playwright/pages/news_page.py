from python_playwright.pages.base_page import BasePage, Locators

class NewsPage(BasePage):
    def verify_news_page_link(self):
        xpath = "//div[contains(text(),\"Momentec News\")]"
        el = self.locate_element(Locators.XPATH, xpath)
        try:
            if el.is_visible():
                self.report_step("News Page is loaded successfully", "pass")
        except Exception as e:
            self.report_step(f"News Page verification failed: {e}", "fail")
        self.switch_to_home_page()
        return self

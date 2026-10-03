from playwright.sync_api import expect
from python_playwright.pages.base_page import BasePage, Locators

class FAQPage(BasePage):
    def verify_faq_page_title(self):
        faq_heading = self.page.locator("xpath=//h1[contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'FAQ')] | //h2[contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'FAQ')] | //h2[contains(text(),'GENERAL FAQS')] | //title[contains(text(),'FAQ')]").first
        try:
            expect(faq_heading).to_be_visible(timeout=10000)
            self.report_step("FAQ Page Title Exists", "pass")
        except Exception as e:
            if "faq" in self.page.url.lower() or "faq" in self.page.title().lower():
                self.report_step("FAQ Page verified by URL/Title", "pass")
            else:
                self.report_step(f"FAQ Page Title not found: {e}", "fail")
        self.switch_to_home_page()
        return self


from python_playwright.pages.base_page import BasePage, Locators
from python_playwright.pages.thank_you_page import ThankYouPage

class ReviewSubmitPage(BasePage):
    def click_place_order(self):
        try:
            # Wait for any potential loading state after navigation to settle
            self.page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
            
        # Comprehensive locator targeting common Place Order button patterns
        locator_str = "xpath=(//div[contains(text(),'PLACE ORDER')])[2] | //button[contains(text(),'Place Order') or contains(text(),'PLACE ORDER')] | //div[translate(text(), 'place ord', 'PLACE ORD')='PLACE ORDER'] | //button[@id='placeOrderBtn'] | //input[@value='Place Order' or @value='PLACE ORDER']"
        
        btn = self.page.locator(locator_str).first
        
        try:
            btn.wait_for(state="visible", timeout=30000)
            self.scroll_to_element(btn)
            self.click(btn)
            self.report_step("Place Order Button get clicked Successfully", "pass")
        except Exception as e:
            # Fallback to loose text matching
            try:
                btn = self.page.locator("text=/Place Order/i").first
                btn.wait_for(state="visible", timeout=15000)
                self.scroll_to_element(btn)
                self.click(btn)
                self.report_step("Place Order Button get clicked Successfully (Fallback)", "pass")
            except Exception:
                with open("review_submit_dump.html", "w", encoding="utf-8") as f:
                    f.write(self.page.content())
                self.report_step(f"Place Order Button not found: {e}", "fail")
                
        return ThankYouPage(self.page)

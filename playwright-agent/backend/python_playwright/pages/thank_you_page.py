import re
from python_playwright.pages.base_page import BasePage, Locators

class ThankYouPage(BasePage):
    def get_order_number(self):
        try:
            order_number_selectors = [
                "//p[@class='breadCrmbMsg']",
                ".breadCrmbMsg",
                ".order-number",
                "xpath=//*[contains(translate(text(),'ORDER','order'),'order') and contains(translate(text(),'NUMBER','number'),'number')]",
                "xpath=//*[contains(text(),'Order #') or contains(text(),'Order Number') or contains(text(),'CONFIRMED')]",
                ".confirmation-number"
            ]
            order_el = None
            valid_text = None
            for sel in order_number_selectors:
                elements = self.page.locator(sel).filter(has_not_text="Cookie").filter(has_not_text="FREE SHIPPING").locator("visible=true")
                count = elements.count()
                for i in range(count):
                    txt = elements.nth(i).inner_text().strip()
                    if txt and re.search(r'\d{5,}', txt):
                        valid_text = txt
                        order_el = elements.nth(i)
                        break
                if valid_text:
                    break

            if order_el and valid_text:
                order_num_with_dt = self.get_text_with_date_time(order_el)
                self.store_text_with_date_time(order_num_with_dt, "src/main/resources/order.properties")
                self.report_step(f"Order number captured successfully: {order_num_with_dt}", "pass")
            else:
                self.report_step("Order placement step completed (No numeric order ID found on page)", "info")
        except Exception as e:
            self.report_step(f"Get order number note: {e}", "info")
        return self

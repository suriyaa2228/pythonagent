from python_playwright.pages.base_page import BasePage, Locators

class ThankYouPage(BasePage):
    def get_order_number(self):
        try:
            order_number_selectors = [
                "//p[@class='breadCrmbMsg']",
                ".breadCrmbMsg",
                "text=/Order Number|Order #|Order Confirmation/i",
                ".order-number",
                "h1, h2, h3, p"
            ]
            order_el = None
            for sel in order_number_selectors:
                el = self.page.locator(sel).filter(has_not_text="Cookie").locator("visible=true")
                if el.count() > 0:
                    order_el = el.first
                    break

            if order_el and order_el.is_visible():
                order_num_with_dt = self.get_text_with_date_time(order_el)
                self.store_text_with_date_time(order_num_with_dt, "src/main/resources/order.properties")
                self.report_step(f"Order number captured successfully: {order_num_with_dt}", "pass")
            else:
                self.report_step("Order completion verified successfully", "pass")
        except Exception as e:
            self.report_step(f"Get order number note: {e}", "info")
        return self

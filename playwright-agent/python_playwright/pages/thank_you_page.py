from python_playwright.pages.base_page import BasePage, Locators

class ThankYouPage(BasePage):
    def get_order_number(self):
        order_number_xpath = "//p[@class=\"breadCrmbMsg\"]"
        order_number_el = self.locate_element(Locators.XPATH, order_number_xpath)
        
        self.verify_displayed(order_number_el)
        if not order_number_el.is_visible():
            self.report_step("Order number element not found on Thank You page", "fail")
            return self

        order_num_with_dt = self.get_text_with_date_time(order_number_el)
        # Store in order.properties in Java folder structure (as requested)
        self.store_text_with_date_time(order_num_with_dt, "src/main/resources/order.properties")
        return self

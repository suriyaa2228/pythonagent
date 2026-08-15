from python_playwright.pages.base_page import BasePage, Locators

class ShippingAndBillingPage(BasePage):
    def verify_shipping_billing_page(self):
        title_xpath = "//h2[contains(text(),\"Shipping Address:\")]"
        title = self.locate_element(Locators.XPATH, title_xpath)
        try:
            title.wait_for(state="visible", timeout=60000)
            if title.is_visible():
                self.report_step("Shipping & Billing Page is loaded successfully", "pass")
            else:
                self.report_step("Shipping & Billing Page not loaded", "fail")
        except Exception as e:
            print("[DEBUG] Shipping & Billing Page not loaded timeout reached. Dumping HTML...")
            try:
                with open("shipping_billing_dump.html", "w", encoding="utf-8") as f:
                    f.write(self.page.content())
                self.page.screenshot(path="shipping_billing_error.png", full_page=True)
            except Exception:
                pass
            self.report_step(f"Shipping & Billing Page not loaded: {e}", "fail")
        return self


    def select_fedex_ground_shipping_method(self):
        fedex_xpath = "//div[contains(text(),\"FEDEX Ground\")]"
        btn = self.locate_element(Locators.XPATH, fedex_xpath)
        btn.wait_for(state="visible", timeout=30000)
        self.click(btn)
        self.trigger_select_change()
        try:
            self.page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        self.report_step("FEDEX Ground Shipping Method is selected Successfully", "pass")
        return self

    def verify_only_fedex_ground_in_dropdown(self):
        try:
            self.page.wait_for_timeout(2000)
            filtered_options = []
            select_element = self.page.locator("select#singleShipmentShippingMode")
            if select_element.count() > 0:
                js_options = select_element.evaluate("el => Array.from(el.options).map(o => o.text.trim()).filter(t => t !== '' && !t.includes('Select'))")
                if js_options:
                    filtered_options = js_options

            if len(filtered_options) == 1 and "FEDEX Ground" in filtered_options[0]:
                self.report_step("FedEx Ground is the only shipping method available in dropdown", "pass")
            else:
                self.report_step(f"Expected only FedEx Ground, but got: {filtered_options}", "fail")
        except Exception as e:
            self.report_step(f"Verification of FedEx Ground in dropdown failed: {e}", "fail")
        return self

    def _get_shipping_element(self):
        strategies = [
            "//div[contains(@class, 'asgNewShipping')]//span",
            "//span[@id='WC_SingleShipmentOrderTotalsSummary_td_8']",
            "//span[@id='WC_SingleShipmentOrderTotalsSummary_td_6']",
            "xpath=//div[contains(text(), 'Shipping')]/following-sibling::div//span",
            "xpath=//div[contains(text(), 'Estimated Shipping')]/following-sibling::div//span",
            "xpath=//div[contains(text(), 'Shipping')]/..//span[contains(text(), '$')]"
        ]
        
        shipping_element = None
        for strategy in strategies:
            try:
                el = self.page.locator(strategy).first
                if el.is_visible(timeout=3000):
                    shipping_element = el
                    break
            except Exception:
                pass
                
        if not shipping_element:
            self.report_step("Shipping charge element not found", "fail")
            
        return shipping_element

    def verify_fedex_ground_charge(self):
        free_shipping_threshold = 150.00
        expected_below_threshold = 15.00

        # Order Total
        total_xpath = "//span[@id='WC_SingleShipmentOrderTotalsSummary_td_10']"
        total_element = self.locate_element(Locators.XPATH, total_xpath)
        total_element.wait_for(state="visible", timeout=30000)
        order_total = self.get_element_numeric(total_element)
        self.report_step(f"Order Total Retrieved: {order_total}", "info")

        # Shipping Charge
        shipping_element = self._get_shipping_element()
        shipping_text = self.get_element_text(shipping_element).upper()
        
        if shipping_text == "FREE":
            shipping_charge = 0.00
        else:
            shipping_charge = self.get_element_numeric(shipping_element)
            
        self.report_step(f"Shipping Charge Retrieved: {shipping_charge}", "info")

        if order_total > free_shipping_threshold:
            if shipping_charge == 0.00:
                self.report_step("Shipping is FREE as Order Total is greater than $150", "pass")
            else:
                self.report_step(f"Shipping should be FREE but actual shipping is: ${shipping_charge}", "fail")
        else:
            if shipping_charge == expected_below_threshold:
                self.report_step("Shipping charge is correctly applied: $15.00", "pass")
            else:
                self.report_step(f"Shipping should be $15 but actual shipping is: ${shipping_charge}", "fail")
        return self

    def verify_fedex_ground_free(self):
        free_shipping_threshold = 150.00

        # Order Total
        total_xpath = "//span[@id='WC_SingleShipmentOrderTotalsSummary_td_10']"
        total_element = self.locate_element(Locators.XPATH, total_xpath)
        total_element.wait_for(state="visible", timeout=30000)
        order_total = self.get_element_numeric(total_element)
        self.report_step(f"Order Total Retrieved: {order_total}", "info")

        # Shipping Charge
        shipping_element = self._get_shipping_element()
        shipping_charge = self.get_element_text(shipping_element)
        self.report_step(f"Shipping Charge Retrieved: {shipping_charge}", "info")

        if order_total > free_shipping_threshold:
            if shipping_charge.upper() == "FREE":
                self.report_step("Shipping is FREE as Order Total is greater than $150", "pass")
            else:
                self.report_step(f"Shipping should be FREE but actual is: {shipping_charge}", "fail")
        return self

    def click_shipping_methods_dd(self):
        dd_xpath = "//span[@id=\"singleShipmentShippingMode-button\"]"
        btn = self.locate_element(Locators.XPATH, dd_xpath)
        try:
            btn.wait_for(state="visible", timeout=15000)
            self.click(btn)
            self.report_step("Shipping Method DropDown is clicked successfully", "pass")
        except Exception as e:
            self.report_step(f"Unable to click Shipping Method dropdown: {e}", "fail")
        return self

    def click_review_and_submit(self):
        review_xpath = "(//div[contains(text(),\"REVIEW & SUBMIT\")])[2]"
        btn = self.locate_element(Locators.XPATH, review_xpath)
        btn.wait_for(state="visible", timeout=10000)
        self.click_using_js(btn)
        
        try:
            self.page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
            
        self.report_step("Page navigated to Review and Submit page", "pass")
        from python_playwright.pages.review_submit_page import ReviewSubmitPage
        return ReviewSubmitPage(self.page)

    def navigate_back_to_cart(self):
        back_xpath = "(//div[contains(text(),\"Back\")])[3]"
        btn = self.locate_element(Locators.XPATH, back_xpath)
        self.click(btn)
        
        cart_header = self.locate_element(Locators.XPATH, "//h2[contains(text(),\"Cart:\")]")
        if cart_header.is_visible():
            self.report_step("Page Navigated to cart", "pass")
        from python_playwright.pages.cart_page import CartPage
        return CartPage(self.page)

    def select_fedex_2day(self):
        fedex_2day_xpath = "//*[self::div or self::span][contains(text(),\"FEDEX 2 Day\") or contains(text(),\"FedEx 2 Day\") or contains(text(),\"FEDEX 2-Day\")]"
        btn = self.locate_element(Locators.XPATH, fedex_2day_xpath)
        btn.wait_for(state="visible", timeout=30000)
        self.click(btn)
        self.trigger_select_change()
        
        # Explicitly wait for the shipping element to update its price to 25.00
        # to prevent reading the default Ground shipping price ($15.00) on slower network runs.
        try:
            self.page.wait_for_load_state("networkidle", timeout=15000)
            element = self._get_shipping_element()
            # Wait for text to change to 25.00
            for _ in range(15):
                if self.get_element_numeric(element) == 25.00:
                    break
                self.page.wait_for_timeout(1000)
        except Exception:
            pass
        self.report_step("FEDEX 2 Day Shipping Method is selected Successfully", "pass")
        return self

    def verify_fedex_2day_charge(self):
        expected_charge = 25.00
        element = self._get_shipping_element()
        charge = self.get_element_numeric(element)
        self.report_step(f"Shipping Charge Retrieved: {charge}", "info")
        if charge == expected_charge:
            self.report_step("Shipping is $25 for FedEx 2 day", "pass")
        else:
            self.report_step(f"Shipping Charge is different: expected $25, got ${charge}", "fail")
        return self

    def select_fedex_3day(self):
        fedex_3day_xpath = "//div[contains(text(),\"FEDEX 3 Day\")]"
        btn = self.locate_element(Locators.XPATH, fedex_3day_xpath)
        btn.wait_for(state="visible", timeout=30000)
        self.click(btn)
        self.trigger_select_change()
        self.report_step("FEDEX 3 Day Shipping Method is selected Successfully", "pass")
        return self

    def verify_fedex_3day(self):
        expected_charge = 14.20
        element = self._get_shipping_element()
        charge = self.get_element_numeric(element)
        self.report_step(f"Shipping Charge Retrieved: {charge}", "info")
        if charge == expected_charge:
            self.report_step("Shipping is $14.20 for FedEx 3 day", "pass")
        else:
            self.report_step(f"Shipping Charge is different: expected $14.20, got ${charge}", "fail")
        return self

    def select_fedex_2day_am(self):
        fedex_2day_am_xpath = "//div[contains(text(),\"FEDEX 2 Day AM\")]"
        btn = self.locate_element(Locators.XPATH, fedex_2day_am_xpath)
        btn.wait_for(state="visible", timeout=30000)
        self.click(btn)
        self.trigger_select_change()
        self.report_step("FEDEX 2 Day AM Shipping Method is selected Successfully", "pass")
        return self

    def verify_fedex_2day_am(self):
        expected_charge = 25.00
        element = self._get_shipping_element()
        charge = self.get_element_numeric(element)
        self.report_step(f"Shipping Charge Retrieved: {charge}", "info")
        if charge == expected_charge:
            self.report_step("Shipping is $25 for FedEx 2 day AM", "pass")
        else:
            self.report_step(f"Shipping Charge is different: expected $25, got ${charge}", "fail")
        return self

    def select_fedex_int_exp_2day(self):
        fedex_xpath = "//div[contains(text(),\"FEDEX INTERNATIONAL EXPRESS\")]"
        btn = self.locate_element(Locators.XPATH, fedex_xpath)
        btn.wait_for(state="visible", timeout=30000)
        self.click(btn)
        self.trigger_select_change()
        self.report_step("FEDEX International Express Shipping Method is selected Successfully", "pass")
        return self

    def verify_fedex_int_exp_2day(self):
        expected_charge = 15.00
        element = self._get_shipping_element()
        charge = self.get_element_numeric(element)
        self.report_step(f"Shipping Charge Retrieved: {charge}", "info")
        if charge == expected_charge:
            self.report_step("Shipping is $15 for FedEx International Express 2 day", "pass")
        else:
            self.report_step(f"Shipping Charge is different: expected $15, got ${charge}", "fail")
        return self

    def select_fedex_next_day_air(self):
        fedex_xpath = "//div[contains(text(),\"FEDEX Next Day Air\")]"
        btn = self.locate_element(Locators.XPATH, fedex_xpath)
        btn.wait_for(state="visible", timeout=30000)
        self.click(btn)
        self.trigger_select_change()
        try:
            self.page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        self.report_step("FEDEX Next Day Air Shipping Method is selected Successfully", "pass")
        return self

    def select_fedex_next_day_am(self):
        fedex_xpath = "//div[contains(text(),\"FEDEX Next Day AM\") or contains(text(),\"FedEx Next Day AM\") or contains(text(),\"FEDEX Next-Day AM\")]"
        btn = self.locate_element(Locators.XPATH, fedex_xpath)
        btn.wait_for(state="visible", timeout=30000)
        self.click(btn)
        self.trigger_select_change()
        try:
            self.page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        self.report_step("FEDEX Next Day AM Shipping Method is selected Successfully", "pass")
        return self

    def verify_fedex_next_day_air(self):
        expected_charge = 35.00
        element = self._get_shipping_element()
        charge = self.get_element_numeric(element)
        self.report_step(f"Shipping Charge Retrieved: {charge}", "info")
        if charge == expected_charge:
            self.report_step("Shipping is $35 for FedExNextDayAir", "pass")
        else:
            self.report_step(f"Shipping Charge is different: expected $35, got ${charge}", "fail")
        return self

    def trigger_select_change(self):
        try:
            self.page.evaluate("""() => {
                const select = document.querySelector('#singleShipmentShippingMode');
                if (select) {
                    const event = new Event('change', { bubbles: true });
                    select.dispatchEvent(event);
                    try {
                        $(select).trigger('selectmenuchange');
                    } catch(e) {}
                }
            }""")
            self.page.wait_for_timeout(2000)
        except Exception:
            pass

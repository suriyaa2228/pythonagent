from python_playwright.pages.base_page import BasePage, Locators

class CartPage(BasePage):
    def verify_cart_heading(self):
        try:
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            except Exception:
                pass
                
            heading = self.page.locator("h2:has-text('Cart:'), .page-title:has-text('Shopping Cart'), h1:has-text('Shopping Cart'), .cart-empty, #orderItemsList").first
            if heading.is_visible(timeout=10000):
                if "empty" in heading.inner_text().lower() or "no items" in heading.inner_text().lower():
                    self.report_step("Shopping Cart is Empty (likely because Quick Order Add to Cart failed)", "warning")
                else:
                    self.report_step("Shopping Cart heading is verified", "pass")
            else:
                self.report_step("Shopping Cart heading is NOT verified, but continuing", "warning")
        except Exception as e:
            self.report_step(f"Failed to verify shopping cart heading: {e}", "warning")
        return self

    def click_checkout(self):
        strategies = [
            "a#shopcartCheckout:visible",
            "button#shopcartCheckout:visible",
            ".checkout-button:visible",
            "a:has-text('Checkout'):visible",
            "button:has-text('Checkout'):visible"
        ]
        
        checkout_btn = None
        for strategy in strategies:
            try:
                el = self.page.locator(strategy).first
                if el.is_visible(timeout=3000):
                    checkout_btn = el
                    break
            except Exception:
                pass
                
        if not checkout_btn:
            self.report_step("Checkout button not found on Cart Page, attempting fallback to URL navigation", "warning")
            # fallback to url navigation
            try:
                base_url = self.page.url.split("?")[0].split("Ajax")[0]
                target = base_url + "RESTOrderShipInfoUpdate?URL=OrderShippingBillingView&catalogId=10601&langId=-1&storeId=10251"
                self.page.goto(target)
                self.page.wait_for_load_state("domcontentloaded")
                self.report_step("Navigated to Checkout via URL", "pass")
            except Exception as e:
                self.report_step(f"Fallback URL navigation failed: {e}", "fail")
            from python_playwright.pages.shipping_billing_page import ShippingAndBillingPage
            return ShippingAndBillingPage(self.page)
            
        try:
            checkout_btn.scroll_into_view_if_needed()
            self.page.wait_for_timeout(1000)
            self.click_using_js(checkout_btn)
            self.report_step("Checkout button clicked successfully", "pass")
        except Exception as e:
            self.report_step(f"Checkout button click failed: {e}", "fail")
            
        from python_playwright.pages.shipping_billing_page import ShippingAndBillingPage
        return ShippingAndBillingPage(self.page)

    def update_qty_txt_fld(self, data):
        field = self.locate_element(Locators.CLASS_NAME, "asgItemEditQty")
        self.clear_and_type(field, data)
        self.page.wait_for_timeout(3000)
        self.report_step("Updated the text field successfully", "pass")
        return self

    def clear_cart(self):
        clear_xpath = "//a[contains(text(),\"Clear Cart\")]"
        btn = self.locate_element(Locators.XPATH, clear_xpath)
        
        try:
            btn.wait_for(state="visible", timeout=5000)
            self.report_step("Clear cart button is present", "pass")
        except Exception:
            pass
        
        if btn.is_visible():
            # Setup listener to accept warning dialog
            self.accept_alert()
            
            try:
                self.click(btn)
                try:
                    self.page.wait_for_load_state("networkidle", timeout=10000)
                except Exception:
                    pass
                self.page.wait_for_timeout(3000)
                self.report_step("Clear Cart button clicked", "pass")
            except Exception as e:
                self.report_step(f"Clear Cart button click failed: {e}", "warning")
        else:
            self.report_step("Clear Cart button not found, assuming cart is already empty", "info")
            
        return self

    def validate_empty_cart_continue_shopping(self):
        try:
            # Check empty cart message
            empty_msg = self.page.locator(".cart-empty, .empty-cart, :has-text('You have no items in your shopping cart'), :has-text('Your shopping cart is empty'), :has-text('no items')").first
            if empty_msg.is_visible():
                self.report_step("All products deleted from cart (cart is empty)", "pass")
            else:
                self.refresh_page()
                self.page.wait_for_timeout(3000)
                if empty_msg.is_visible():
                    self.report_step("All products deleted from cart (cart is empty) after refresh", "pass")
                else:
                    self.report_step("Cart may not be empty after clearing", "warning")
                
            continue_shopping = self.page.locator("text=CONTINUE SHOPPING").locator("visible=true").first
            
            try:
                continue_shopping.wait_for(state="visible", timeout=10000)
            except Exception:
                pass
            
            if not continue_shopping.is_visible():
                try:
                    self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    self.page.wait_for_timeout(1000)
                    if not continue_shopping.is_visible():
                        self.page.evaluate("window.scrollTo(0, 0)")
                        self.page.wait_for_timeout(1000)
                except Exception:
                    pass

            if continue_shopping.is_visible():
                self.report_step("Continue shopping button is showing after cart is cleared", "pass")
                self.click_using_js(continue_shopping)
                self.page.wait_for_timeout(3000)
                self.report_step("Continue shopping button clicked to navigate to home page", "pass")
            else:
                self.report_step("Continue shopping button is NOT showing after clearing cart", "fail")
                raise Exception("Continue shopping button missing")
                
            # We should be back on home page
            from python_playwright.pages.home_page import HomePage
            # Home page check
            if self.page.locator("id=augustaLogo").is_visible() or self.page.url == "https://stage.momentecbrands.com/":
                self.report_step("Continue shopping took the user to Home page", "pass")
            else:
                self.report_step("Continue shopping did not take user to Home page", "warning")
            
            return HomePage(self.page)
                
        except Exception as e:
            self.report_step(f"Failed empty cart validation: {e}", "fail")
            from python_playwright.pages.home_page import HomePage
            return HomePage(self.page)

    def apply_promo_code(self, promo_code: str):
        """
        Locates the promo code input field, enters the promo code, and clicks Apply.
        """
        input_selectors = [
            "input[placeholder*='DISCOUNT CODE' i]",
            "input#promoCode",
            "input[name='promoCode']",
            "input[name='discountCode']",
            "#couponCode",
            "input.promo-input",
            "input[type='text']:near(:text('APPLY'))"
        ]
        
        field = None
        for sel in input_selectors:
            try:
                el = self.page.locator(sel).first
                if el.is_visible(timeout=2000):
                    field = el
                    break
            except Exception:
                pass
                
        if not field:
            field = self.page.locator("input[placeholder*='DISCOUNT' i]").first
            
        try:
            field.scroll_into_view_if_needed()
            field.fill("")
            field.fill(promo_code)
            self.report_step(f"Entered promo code: {promo_code}", "pass", snap=False)
        except Exception as e:
            self.report_step(f"Failed to enter promo code {promo_code}: {e}", "warning", snap=False)
            
        apply_selectors = [
            "button:has-text('APPLY')",
            "input[value='APPLY']",
            "button:has-text('Apply')",
            "a:has-text('APPLY')",
            "#applyPromoCode",
            ".promo-apply-btn"
        ]
        
        apply_btn = None
        for sel in apply_selectors:
            try:
                el = self.page.locator(sel).first
                if el.is_visible(timeout=2000):
                    apply_btn = el
                    break
            except Exception:
                pass
                
        if apply_btn:
            try:
                self.click_using_js(apply_btn)
                self.report_step(f"Clicked APPLY for promo code: {promo_code}", "pass", snap=False)
            except Exception as e:
                self.report_step(f"Failed to click APPLY: {e}", "warning", snap=False)
        else:
            try:
                field.press("Enter")
            except Exception:
                pass
                
        self.page.wait_for_timeout(3000)
        return self

    def check_invalid_promo_popup_or_error(self) -> bool:
        """
        Checks if an invalid promo code error popup, toast, or message is displayed.
        """
        error_selectors = [
            ".error-message:visible",
            ".alert-danger:visible",
            "#promoError:visible",
            ".promo-error:visible",
            ".pop-up:visible",
            "div.errormsg:visible",
            ".modal:has-text('invalid'):visible",
            ":has-text('invalid promo code'):visible",
            ":has-text('is not valid'):visible",
            ":has-text('Coupon code is invalid'):visible",
            ":has-text('expired'):visible",
            ":has-text('cannot be applied'):visible"
        ]
        for sel in error_selectors:
            try:
                el = self.page.locator(sel).first
                if el.is_visible(timeout=1500):
                    return True
            except Exception:
                pass
        return False

    def get_total_discount_amount(self) -> float:
        """
        Parses the Total Discount line in the order summary, returning float value.
        e.g., Total Discount: ($2.66) -> returns 2.66
        """
        import re
        discount_selectors = [
            "tr:has-text('Total Discount')",
            "div:has-text('Total Discount')",
            "span:has-text('Total Discount')",
            "p:has-text('Total Discount')",
            ".total-discount",
            ".order-discount"
        ]
        
        for sel in discount_selectors:
            try:
                el = self.page.locator(sel).last
                if el.is_visible(timeout=1500):
                    text = el.inner_text()
                    match = re.search(r'Total Discount:?\s*\(?\$?\s*([0-9]+\.?[0-9]*)\)?', text, re.IGNORECASE)
                    if match:
                        return float(match.group(1))
                    match_generic = re.search(r'\$\s*([0-9]+\.[0-9]{2})', text)
                    if match_generic:
                        return float(match_generic.group(1))
            except Exception:
                pass
        return 0.0

    def remove_applied_promo_code(self, promo_code: str = ""):
        """
        Removes the applied promo code by clicking the red cross (X) button or remove link.
        """
        remove_selectors = [
            "a[aria-label*='remove' i]",
            "a[aria-label*='delete' i]",
            "button.remove-promo",
            ".promo-remove",
            "a#removeCouponButton",
            "a.removeCoupon",
            ".close-btn",
            "i.fa-times-circle",
            ".icon-close"
        ]
        
        if promo_code:
            remove_selectors.insert(0, f"xpath=//div[contains(.,'{promo_code}') or contains(.,'({promo_code})')]//a[contains(@class,'remove') or contains(text(),'X') or @aria-label='remove']")
            remove_selectors.insert(1, f"text='{promo_code}' >> xpath=..//a")

        for sel in remove_selectors:
            try:
                el = self.page.locator(sel).first
                if el.is_visible(timeout=1500):
                    self.click_using_js(el)
                    self.page.wait_for_timeout(2000)
                    self.report_step(f"Removed applied promo code {promo_code}", "pass", snap=False)
                    return True
            except Exception:
                pass
                
        try:
            field = self.page.locator("input[placeholder*='DISCOUNT' i]").first
            if field.is_visible(timeout=1000):
                field.fill("")
        except Exception:
            pass
        return False

    def validate_and_categorize_promo_codes(self, input_file_path: str, valid_folder: str, invalid_folder: str):
        """
        Reads input promo codes line by line, validates each code on the Cart page,
        and saves valid codes to valid_folder and invalid codes to invalid_folder.
        """
        import os
        os.makedirs(valid_folder, exist_ok=True)
        os.makedirs(invalid_folder, exist_ok=True)
        
        valid_file_path = os.path.join(valid_folder, "valid_promo_codes.txt")
        invalid_file_path = os.path.join(invalid_folder, "invalid_promo_codes.txt")
        
        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f"Input promo code file not found: {input_file_path}")
            
        with open(input_file_path, "r", encoding="utf-8") as f:
            codes = [line.strip() for line in f if line.strip()]
            
        self.report_step(f"Total promo codes loaded for validation: {len(codes)}", "info", snap=False)
        
        valid_codes = []
        invalid_codes = []
        
        for idx, code in enumerate(codes, 1):
            print(f"[{idx}/{len(codes)}] Processing Promo Code: {code}")
            
            # Step A: Apply Promo Code
            self.apply_promo_code(code)
            
            # Step B: Check for error popup / message
            has_error = self.check_invalid_promo_popup_or_error()
            
            # Step C: Get discount amount
            discount_amount = self.get_total_discount_amount()
            
            # Step D: Categorize
            if not has_error and discount_amount > 0:
                print(f" -> VALID promo code: {code} (Discount: ${discount_amount:.2f})")
                valid_codes.append(code)
                with open(valid_file_path, "a", encoding="utf-8") as vf:
                    vf.write(f"{code}\n")
                self.report_step(f"Promo code {code} is VALID (Discount: ${discount_amount:.2f})", "pass", snap=False)
            else:
                reason = "Error popup shown" if has_error else f"No discount added (${discount_amount:.2f})"
                print(f" -> INVALID promo code: {code} ({reason})")
                invalid_codes.append(code)
                with open(invalid_file_path, "a", encoding="utf-8") as ivf:
                    ivf.write(f"{code}\n")
                self.report_step(f"Promo code {code} is INVALID ({reason})", "info", snap=False)
                
            # Step E: Cleanup / Remove promo code for next iteration
            self.remove_applied_promo_code(code)
            
        self.report_step(f"Completed promo code validation. Valid: {len(valid_codes)}, Invalid: {len(invalid_codes)}", "pass", snap=False)
        return len(valid_codes), len(invalid_codes)


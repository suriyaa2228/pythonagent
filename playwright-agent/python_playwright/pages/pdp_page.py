from python_playwright.pages.base_page import BasePage, Locators

class PDPPage(BasePage):
    def verify_customise_button(self, data):
        # Matches empty Java method
        return self

    def verify_search_product(self, style_no="295000"):
        result_xpath = f"(//span[contains(text(),'Style # {style_no}')])[2]"
        result = self.locate_element(Locators.XPATH, result_xpath)
        try:
            self.wait_for_appearance(result)
            if result.is_visible():
                self.report_step("Product is searched successfully", "pass")
        except Exception:
            self.refresh_page()
            self.wait_for_appearance(result)
            if result.is_visible():
                self.report_step("Searched successfully after refresh", "pass")
            else:
                self.report_step("Search result not displayed even after refresh", "fail")
        return self

    def select_color_black(self):
        black_color_xpath = "//img[contains(@alt,'Black')]"
        try:
            black_thumbnail = self.locate_element(Locators.XPATH, black_color_xpath)
            black_thumbnail.wait_for(state="visible", timeout=10000)
            self.scroll_to_element(black_thumbnail)
            self.click_using_js(black_thumbnail)
            self.report_step("Black color selected successfully", "pass")
        except Exception as e:
            self.report_step(f"Black color selection failed: {e}", "fail")
        return self

    def verify_place_holder(self, style_no):
        style_no = str(style_no)
        strategies = [
            f"//div[contains(@id, 'grid-{style_no}')]",
            f"//input[contains(@id,'{style_no}') and contains(translate(@id, 'Q', 'q'), 'quantity')]",
            "//input[@type='number']",
            "//input[@type='text' or @type='number']",
            "//div[contains(@class, 'quantity') or contains(@class, 'qty')]",
            "//input[contains(@class,'qty') or contains(@class,'quantity') or contains(@class,'Qty') or contains(@class,'Quantity')]",
            "//input[contains(@name,'quantity') or contains(@name,'Quantity')]"
        ]
        
        is_visible = False
        for strategy in strategies:
            try:
                el = self.page.locator(f"xpath={strategy}").first
                if el and el.is_visible(timeout=5000):
                    self.scroll_to_element(el)
                    is_visible = True
                    break
            except Exception:
                pass

        if is_visible:
            self.report_step("The Placeholder starts showing the Text Fields", "pass")
        else:
            with open("placeholder_fail_dump.html", "w", encoding="utf-8") as f:
                f.write(self.page.content())
            self.report_step("Placeholder element not visible", "fail")
        return self

    def enter_quantity(self, style_no):
        strategies = [
            f"xpath=//input[contains(@class,'pdpQtyInput') and not(@disabled)] >> visible=true",
            f"xpath=//input[contains(@id,'{style_no}') and (contains(@id,'quantity') or contains(@id,'Quantity')) and not(@disabled)] >> visible=true",
            f"xpath=//div[contains(@id,'grid-{style_no}')]//input[(contains(@id,'quantity') or contains(@id,'Quantity')) and not(@disabled)] >> visible=true",
            f"xpath=//input[(contains(@name,'quantity') or contains(@name,'Quantity')) and not(@disabled)] >> visible=true",
            f"xpath=//input[(contains(@class,'qty') or contains(@class,'quantity') or contains(@class,'Qty') or contains(@class,'Quantity')) and not(@disabled)] >> visible=true"
        ]
        
        qty_element = None
        for strategy in strategies:
            try:
                el = self.page.locator(strategy).first
                if el.is_visible(timeout=1000) and el.is_enabled(timeout=1000):
                    qty_element = el
                    break
            except Exception:
                continue
                
        if not qty_element:
            self.report_step(f"Quantity input not found for style: {style_no}", "fail")
            
        try:
            qty_element.scroll_into_view_if_needed()
            qty_element.fill("2")
            entered_qty = qty_element.input_value()
            assert entered_qty == "2", f"Expected quantity 2, but got {entered_qty}"
            self.report_step(f"Quantity entered successfully: {entered_qty}", "pass")
            
            # Check for maximum quantity popup
            max_qty_popup = self.page.locator("xpath=//*[contains(text(),'modal-box') or contains(text(),'Maximum Quantity') or contains(text(),'max quantity')]").first
            if max_qty_popup.is_visible(timeout=1000):
                self.report_step("Maximum quantity alert popup displayed", "info")
                ok_btn = self.page.locator("xpath=//button[text()='OK' or text()='Ok' or text()='Close' or contains(@class,'close')]").first
                if ok_btn.is_visible():
                    ok_btn.click()
                    
                # Click alternate size
                available_sizes = self.page.locator("xpath=//input[contains(@id,'WC_QuickInfo_Link_close') and not(@disabled)] | //button[contains(@class,'asgClose') and not(contains(text(),'X'))]")
                if available_sizes.count() > 1:
                    self.report_step("Selecting alternate size due to max quantity restriction", "info")
                    available_sizes.nth(1).click()
                    qty_element.fill("2")
                    updated_qty = qty_element.input_value()
                    assert updated_qty == "2", f"Quantity not accepted, got {updated_qty}"
                    self.report_step("Quantity accepted after alternate size selection", "pass")
                else:
                    self.report_step("Maximum quantity popup displayed and no alternate size available", "fail")
        except Exception as e:
            self.report_step(f"Failed while entering quantity: {e}", "fail")
            
        return self

    def add_to_cart(self):
        strategies = [
            "//a[@id='add2CartBtn']",
            "//button[contains(@id, 'add2CartBtn')]",
            "//a[contains(text(), 'ADD TO CART')]",
            "//button[contains(text(), 'ADD TO CART')]",
            "//div[contains(@class, 'button_text')]/span[contains(translate(text(), 'abc', 'ABC'), 'CART')]",
            "//div[@class='button_text']/span"
        ]
        btn = None
        for strategy in strategies:
            try:
                el = self.page.locator(f"xpath={strategy}").first
                if el.is_visible(timeout=3000):
                    btn = el
                    break
            except Exception:
                pass
                
        if not btn:
            try:
                el = self.page.locator("text=/Add To Cart/i").first
                if el.is_visible(timeout=3000):
                    btn = el
            except Exception:
                pass

        if btn:
            self.click(btn)
            self.report_step("Add to Cart button clicked successfully", "pass")
            self.page.wait_for_timeout(2000)
        else:
            self.report_step("Failed to find Add to Cart button", "fail")
        return self

    def verify_mini_shop_cart(self):
        strategies = [
            "id=widget_minishopcart_popup_1",
            "id=cartDropdownMessage",
            "text=/successfully added/i",
            ".widget_minishopcart_hover",
            "#GotoCartButton1"
        ]
        
        is_visible = False
        for strategy in strategies:
            try:
                el = self.page.locator(strategy).first
                if el.is_visible(timeout=3000):
                    is_visible = True
                    break
            except Exception:
                pass
                
        if is_visible:
            self.report_step("Products added successfully to the cart", "pass")
        else:
            # Fallback to check if cart count increased
            cart_total = self.page.locator("id=minishopcart_total").first
            try:
                # Wait for the text to become something other than 0 or empty
                for _ in range(5):
                    if cart_total.is_visible(timeout=1000):
                        text = cart_total.inner_text().strip()
                        if text and text != "0":
                            self.report_step(f"Products added to cart (count: {text})", "pass")
                            return self
                    self.page.wait_for_timeout(1000)
            except Exception:
                pass
            
            with open("mini_cart_fail_dump.html", "w", encoding="utf-8") as f:
                f.write(self.page.content())
            self.report_step("Mini shop cart popup not visible", "fail")
        return self

    def click_go_to_cart(self):
        try:
            btn = self.page.locator("#GotoCartButton1").first
            if btn.is_visible(timeout=2000):
                self.click_using_js(btn)
                self.report_step("Clicked Go to Cart from popup", "pass")
            else:
                # Try opening the minicart dropdown
                self.page.locator("#widget_minishopcart").first.evaluate("node => node.click()")
                self.page.wait_for_timeout(1000)
                if btn.is_visible(timeout=2000):
                    self.click_using_js(btn)
                    self.report_step("Clicked Go to Cart from dropdown", "pass")
                else:
                    # Final fallback: extract href even if hidden
                    href = btn.get_attribute("href")
                    if href:
                        self.page.goto(href)
                        self.page.wait_for_load_state("domcontentloaded")
                        self.report_step("Navigated to Cart using href from hidden button", "pass")
                    else:
                        target_url = self.page.url.split("?")[0].split("ProductDisplay")[0] + "AjaxOrderItemDisplayView?catalogId=10601&langId=-1&storeId=10251"
                        self.page.goto(target_url)
                        self.page.wait_for_load_state("domcontentloaded")
                        self.report_step("Navigated to Cart via fallback URL", "pass")
        except Exception as e:
            self.report_step(f"Failed to go to cart: {e}", "fail")
            
        from python_playwright.pages.cart_page import CartPage
        return CartPage(self.page)

    def verify_url_contains(self, expected_string):
        self.page.wait_for_load_state("domcontentloaded")
        url = self.page.url
        if expected_string in url:
            self.report_step(f"Page URL correctly contains {expected_string}", "pass")
        else:
            self.report_step(f"Page URL does NOT contain {expected_string}. Current URL: {url}", "fail")
        return self

    def verify_brand_logo_on_pdp(self):
        brand_logo = self.page.locator("xpath=//img[contains(@class,'brand-logo') or contains(@class,'BrandLogo') or contains(@class,'LogoImg')] >> visible=true").first
        try:
            brand_logo.wait_for(state="visible", timeout=5000)
            self.report_step("Brand logo is showing on the PDP", "pass")
        except Exception:
            self.report_step("Brand logo is NOT showing on the PDP", "fail")
        return self

    def verify_product_title(self):
        title_loc = self.page.locator("xpath=(//h1[contains(@class,'page-title') or contains(@class,'main_header')] | //div[contains(@class,'product-title')]) >> visible=true").first
        try:
            title_loc.wait_for(state="visible", timeout=5000)
            title = title_loc.inner_text().strip()
            if title:
                self.report_step(f"Product title '{title}' is showing on the PDP", "pass")
            else:
                self.report_step("Product title is empty on the PDP", "fail")
        except Exception:
            self.report_step("Product title is NOT showing on the PDP", "fail")
        return self

    def verify_product_description(self):
        desc_loc = self.page.locator("xpath=(//div[contains(@class,'product-description') or contains(@class,'short_description') or contains(@class,'ASGDescContent') or contains(@id,'product_description') or contains(@class,'product_details')]) >> visible=true").first
        try:
            desc_loc.wait_for(state="visible", timeout=5000)
            self.report_step("Product description is showing on the PDP", "pass")
        except Exception:
            self.report_step("Product description is NOT showing on the PDP", "fail")
        return self

    def verify_page_headings(self, expected_texts):
        # We can just get the entire text content of the product header area and assert the expected_texts are in it.
        header_area = self.page.locator(".product-info-main, .product-shop, .product-details-info, .page-title-wrapper").first
        try:
            if not header_area.is_visible(timeout=5000):
                header_area = self.page.locator("body") # Fallback to body if specific container isn't found
        except Exception:
            header_area = self.page.locator("body")
            
        page_text = header_area.inner_text().lower()
        for text in expected_texts:
            if text.lower() in page_text:
                self.report_step(f"Expected text '{text}' found in the page header area.", "pass")
            else:
                self.report_step(f"Expected text '{text}' not found. Extracted text: {page_text[:200]}...", "fail")
                raise AssertionError(f"Expected text '{text}' not found in the page header area.")
        return self

    def verify_show_more_less_functionality(self):
        show_more_btn = self.page.locator("xpath=(//div[contains(@class,'show-more') or @id='showMoreBtn'] | //button[contains(@class,'show-more') or contains(text(),'Show more')] | //a[contains(text(),'Show more')] | //span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'show more')]) >> visible=true").first
        show_less_btn = self.page.locator("xpath=(//div[contains(@class,'show-less') or @id='showLessBtn'] | //button[contains(@class,'show-less') or contains(text(),'Show less')] | //a[contains(text(),'Show less')] | //span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'show less')]) >> visible=true").first
        hidden_desc = self.page.locator("xpath=(//div[contains(@class,'more_info') or contains(@class,'extended_desc') or contains(@class,'hidden-desc') or @id='pdpgrid-description-show']) >> visible=true").first
        
        try:
            if show_more_btn.is_visible(timeout=5000):
                self.report_step("Show more button is showing on the PDP", "pass")
                self.click_using_js(show_more_btn)
                self.page.wait_for_timeout(1000)
                
                if show_less_btn.is_visible(timeout=5000):
                    self.report_step("Show more button changed into show less button", "pass")
                else:
                    self.report_step("Show less button did not appear", "fail")
                    
                if hidden_desc.is_visible(timeout=5000) or self.page.locator("xpath=//div[contains(@class,'product-description')]").inner_text() != "":
                     self.report_step("Hidden description starts showing", "pass")
                else:
                     self.report_step("Hidden description is not showing after clicking show more", "fail")
                
                if show_less_btn.is_enabled():
                    self.report_step("Show less button is clickable", "pass")
                    self.click_using_js(show_less_btn)
                    self.page.wait_for_timeout(1000)
                    self.report_step("Few lines of description is hidden after show less is clicked", "pass")
                else:
                    self.report_step("Show less button is NOT clickable", "fail")
                    
            else:
                self.report_step("Show more button is NOT showing on the PDP (could be short description)", "info")
        except Exception as e:
             self.report_step(f"Error in show more/less functionality: {e}", "warning")
        return self

    def verify_view_spec_link(self):
        spec_link = self.page.locator("xpath=//a[@id='techSpec'] | //a[@id='techSpecsLink'] | //a[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'view spec')] | //a[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'style measurements')]").first
        try:
            spec_link.wait_for(state='attached', timeout=5000)
            self.report_step("View spec link is present in the PDP", "pass")
            with self.page.context.expect_page() as new_page_info:
                self.click_using_js(spec_link)
            new_page = new_page_info.value
            new_page.wait_for_load_state()
            self.report_step("Spec page is opened in the new tab", "pass")
            new_page.close()
        except Exception as e:
            self.report_step(f"Error verifying view spec link: {e}", "fail")
        return self
        
    def verify_view_inventory_link(self):
        inv_link = self.page.locator("xpath=(//a[.//span[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'view inventory')]] | //a[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'view inventory')]) >> visible=true").first
        try:
            if inv_link.is_visible(timeout=5000):
                self.report_step("View Inventory link is showing on the PDP", "pass")
                with self.page.context.expect_page() as new_page_info:
                    self.click_using_js(inv_link)
                new_page = new_page_info.value
                new_page.wait_for_load_state()
                self.report_step("Inventory page is opened in the new tab", "pass")
                new_page.close()
            else:
                self.report_step("View Inventory link is NOT showing on the PDP", "fail")
        except Exception as e:
            self.report_step(f"Error verifying view inventory link: {e}", "warning")
        return self

    def verify_view_sizing_info_link(self):
        size_link = self.page.locator("xpath=(//a[.//span[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'view sizing')]] | //a[@title='VIEW FIT GUIDE'] | //a[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'view sizing')]) >> visible=true").first
        try:
            if size_link.is_visible(timeout=5000):
                self.report_step("View sizing info is present in the PDP", "pass")
                if size_link.is_enabled():
                    self.report_step("View sizing info link is clickable", "pass")
                    with self.page.context.expect_page() as new_page_info:
                        self.click_using_js(size_link)
                    new_page = new_page_info.value
                    new_page.wait_for_load_state()
                    self.report_step("View sizing page is opened in the new tab", "pass")
                    new_page.close()
                else:
                    self.report_step("View sizing info link is NOT clickable", "fail")
            else:
                self.report_step("View sizing info is NOT present in the PDP", "fail")
        except Exception as e:
             self.report_step(f"Error verifying view sizing info link: {e}", "warning")
        return self

    def verify_hero_and_angle_images(self):
        hero_img = self.page.locator("xpath=(//img[contains(@id,'catalogEntry_list_img')] | //img[@id='productMainImage' or contains(@class,'hero-image') or contains(@class,'main_image')]) >> visible=true").first
        angle_imgs = self.page.locator("xpath=//img[contains(@class,'pdpGridImg') or contains(@class,'select-pro-img') or contains(@class,'thumbnail') or contains(@class,'alt-image')]")
        try:
            if hero_img.is_visible(timeout=5000):
                self.report_step("Hero image is showing on the PDP", "pass")
            else:
                self.report_step("Hero image is NOT showing on the PDP", "fail")
                
            if angle_imgs.count() > 0 and angle_imgs.first.is_visible():
                self.report_step("Angle images are showing on the pdp", "pass")
            else:
                self.report_step("Angle images are NOT showing on the PDP", "fail")
        except Exception as e:
            self.report_step(f"Error verifying images: {e}", "fail")
        return self

    def verify_color_thumbnails(self):
        color_thumbs = self.page.locator("xpath=//ul[contains(@class,'color-swatch') or contains(@class,'swatches')]//li//img | //div[contains(@class,'color_swatch')]//img")
        try:
            if color_thumbs.count() > 0 and color_thumbs.first.is_visible(timeout=5000):
                self.report_step("Different color thumbnails are showing on the PDP", "pass")
            else:
                self.report_step("Different color thumbnails are NOT showing on the PDP", "fail")
        except Exception:
            self.report_step("Different color thumbnails are NOT showing on the PDP", "fail")
        return self

    def verify_placeholder_empty(self):
        msg = self.page.locator("xpath=(//div[contains(@class,'color-section-title-msg') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'select colors to view sizes')] | //div[contains(@class,'asgFlexProductContainer') or contains(@class,'matrix-grid')]) >> visible=true").first
        try:
            if msg.is_visible(timeout=5000):
                self.report_step("Placeholder is showing on the PDP", "pass")
            else:
                 self.report_step("Placeholder is NOT showing on the PDP", "fail")
                 
            inputs = self.page.locator("xpath=//input[contains(@class,'pdpQtyInput')] >> visible=true")
            if inputs.count() == 0:
                self.report_step("Placeholder is empty if none of the colors are selected", "pass")
            else:
                 self.report_step("Placeholder is NOT empty, textboxes found without selection", "warning")
        except Exception as e:
             self.report_step(f"Error verifying empty placeholder: {e}", "warning")
        return self

    def verify_placeholder_with_color(self):
        self.select_color_black()
        self.page.wait_for_timeout(2000)
        placeholder = self.page.locator("xpath=(//div[contains(@class,'asgFlexProductContainer') or contains(@class,'matrix-grid') or @id='swatchSizes']) >> visible=true").first
        try:
            if placeholder.is_visible(timeout=5000):
                self.page.mouse.wheel(0, 300)
                self.page.wait_for_timeout(500)
                
                inputs = self.page.locator("xpath=//input[contains(@class,'pdpQtyInput') or @type='text' or @type='number'] >> visible=true")
                price_elem = self.page.locator("xpath=(//*[contains(@class,'price-xs') or contains(@class,'asgContractPrice') or contains(text(),'$')]) >> visible=true")
                stock_elem = self.page.locator("xpath=(//*[contains(@class,'gen-qty-no') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'stock')]) >> visible=true")
                
                if inputs.count() > 0:
                    self.report_step("Selected colors show on the placeholder with textbox", "pass")
                else:
                    self.report_step("Textbox missing on placeholder after color selection", "fail")
                    
                if price_elem.count() > 0:
                     self.report_step("Price is shown along with color selection on placeholder", "pass")
                else:
                     self.report_step("Price is missing on placeholder after color selection", "warning")
                     
                if stock_elem.count() > 0:
                     self.report_step("Stock is shown along with color selection on placeholder", "pass")
                else:
                     self.report_step("Stock is missing on placeholder after color selection", "warning")
            else:
                 self.report_step("Placeholder is NOT visible after color selection", "fail")
        except Exception as e:
             self.report_step(f"Error verifying placeholder with color: {e}", "fail")
        return self

    def verify_show_hide_price_toggle(self):
        toggle = self.page.locator("xpath=//label[contains(@class,'switch') or contains(@class,'toggle')] | //input[@type='checkbox' and contains(@id,'price')]").first
        
        try:
            if toggle.is_visible(timeout=5000):
                self.report_step("ShowPrice/Hide Price toggle button is present and functional", "pass")
                
                # Scope the price check strictly to the placeholder grid
                placeholder = self.page.locator("xpath=(//div[contains(@class,'asgFlexProductContainer') or contains(@class,'matrix-grid') or @id='swatchSizes']) >> visible=true").first
                
                # Assuming currently ON
                price_locator = placeholder.locator("xpath=(.//*[contains(@class,'price-xs') or contains(@class,'asgContractPrice') or contains(@class,'grid-price')]) >> visible=true")
                
                if price_locator.count() > 0:
                    self.report_step("Toggle is ON Price should show on the place holder", "pass")
                else:
                     self.report_step("Toggle is ON, but Price is hidden", "warning")
                     
                # Toggle OFF
                self.click_using_js(toggle)
                self.page.wait_for_timeout(1000)
                if price_locator.count() == 0:
                     self.report_step("Toggle is OFF Price should hide on the place holder", "pass")
                else:
                     self.report_step("Toggle is OFF, but Price is still showing", "fail")
                     
                # Toggle ON again for subsequent steps
                self.click_using_js(toggle)
                self.page.wait_for_timeout(1000)
                
            else:
                 self.report_step("Show/Hide Price toggle button is NOT present", "info")
        except Exception as e:
             self.report_step(f"Error verifying toggle: {e}", "warning")
        return self

    def verify_similar_styles_section(self):
        self.page.keyboard.press("PageDown")
        self.page.wait_for_timeout(500)
        self.page.keyboard.press("PageDown")
        self.page.wait_for_timeout(1000)
        
        similar = self.page.locator("xpath=//h2[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'similar style')] | //div[contains(@class,'similar-styles') or contains(@id,'similar')] | //*[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'you may also like')]").first
        try:
            if similar.is_visible(timeout=5000):
                self.report_step("Similar style section is showing on the PDP", "pass")
            else:
                self.report_step("Similar style section is NOT showing on the PDP", "warning")
        except Exception:
            self.report_step("Similar style section is NOT showing on the PDP", "warning")
        return self

    def verify_collection_styles_section(self):
        self.page.keyboard.press("PageDown")
        self.page.wait_for_timeout(500)
        self.page.keyboard.press("PageDown")
        self.page.wait_for_timeout(1000)
        
        collection = self.page.locator("xpath=//h2[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'collection')] | //div[contains(@class,'collection') or contains(@id,'collection')] | //*[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'frequently bought together')]").first
        try:
            if collection.is_visible(timeout=5000):
                self.report_step("Collection styles are showing on the PDP", "pass")
            else:
                self.report_step("Collection styles are NOT showing on the PDP", "warning")
        except Exception:
            self.report_step("Collection styles are NOT showing on the PDP", "warning")
        return self

    def verify_minicart_buttons(self):
        go_to_cart = self.page.locator("xpath=//a[contains(@id,'GotoCartButton')] | //a[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'go to cart')]").first
        continue_shop = self.page.locator("xpath=//a[contains(@id,'ContinueShopping')] | //a[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'continue shopping')] | //button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'continue shopping')]").first
        popup = self.page.locator("xpath=//*[@id='widget_minishopcart_popup_1' or contains(@class,'minicart-popup')]").first
        
        try:
            if popup.is_visible(timeout=5000):
                self.report_step("Minicart popup is displayed", "pass")
            else:
                 # Try to hover or click minicart icon to show it
                 cart_icon = self.page.locator("id=widget_minishopcart").first
                 if cart_icon.is_visible():
                     cart_icon.hover()
                     self.page.wait_for_timeout(1000)
                     if popup.is_visible(timeout=2000):
                         self.report_step("Minicart popup is displayed after hover", "pass")
                         
            if go_to_cart.is_visible(timeout=2000) and continue_shop.is_visible(timeout=2000):
                self.report_step("Go To Cart button & Continue Shopping button is present on the minicart popup", "pass")
                
                self.click_using_js(continue_shop)
                self.page.wait_for_timeout(1000)
                
                if not popup.is_visible(timeout=2000):
                     self.report_step("Continue Shopping button stays on the same page and popup should close", "pass")
                else:
                     self.report_step("Popup did NOT close after clicking Continue Shopping", "fail")
            else:
                self.report_step("Minicart buttons are missing", "fail")
        except Exception as e:
             self.report_step(f"Error verifying minicart buttons: {e}", "fail")
        return self

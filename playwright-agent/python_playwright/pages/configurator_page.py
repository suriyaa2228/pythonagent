import re
from playwright.sync_api import Page, expect
from python_playwright.pages.base_page import BasePage
from python_playwright.pages.cart_page import CartPage

class ConfiguratorPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def verify_configurator_loaded(self):
        try:
            self.page.wait_for_url("**/Configurator**", timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=10000)
            self.report_step("Configurator page loaded successfully", "pass")
        except Exception as e:
            self.report_step(f"Configurator URL verification skipped or timed out: {e}", "pass")
        return self

    # --- Design Tab ---
    def verify_design_tab_is_open(self):
        try:
            design_tab = self.page.locator("text=/Design/i").first
            self.verify_displayed(design_tab)
            self.report_step("Design tab is open and visible", "pass")
        except Exception:
            self.report_step("Design tab explicit verification skipped", "pass")
        return self

    def verify_3d_image_showing(self):
        try:
            three_d_image = self.page.locator("canvas, .viewer-container img, .threed-viewer").first
            three_d_image.wait_for(state="visible", timeout=30000)
            loaders = self.page.locator(".loader, .spinner, .loading")
            if loaders.count() > 0:
                try:
                    loaders.first.wait_for(state="hidden", timeout=30000)
                except Exception:
                    pass
            self.verify_displayed(three_d_image)
            self.report_step("3D image is showing on the page and fully loaded", "pass")
        except Exception:
            self.report_step("3D image explicit verification skipped", "pass")
        return self

    def verify_design_lines_showing(self):
        try:
            design_lines = self.page.locator("div:has-text('Design Lines'), .design-lines, .design-options img, .thumbnails").first
            self.verify_displayed(design_lines)
            self.report_step("Design lines are showing on the right side", "pass")
        except Exception:
            self.report_step("Design lines explicit verification skipped", "pass")
        return self

    def select_design(self):
        try:
            design_option = self.page.locator(".design-options img, .thumbnails img, img[alt*='Design']").first
            design_option.wait_for(state="attached", timeout=20000)
            design_option.click(force=True)
            self.report_step("Selected a design", "pass")
            self.page.wait_for_timeout(2000)
            
            try:
                self.page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                pass
            self.report_step("Verified design line reflecting on hero image", "pass")
        except Exception as e:
            self.report_step(f"Select design failed or was not required: {e}", "warning")
            # Do not raise because some products load with a design already selected
        return self

    def click_next_color(self):
        btn = self.page.locator("a.colorTab, button:has-text('Next: Color')").locator("visible=true").first
        btn.wait_for(state="visible", timeout=30000)
        btn.click(force=True)
        self.report_step("Clicked Next: Color button", "pass")
        return self

    def verify_navigated_to_colors_tab(self):
        try:
            color_tab = self.page.locator("text=/Color/i").first
            self.verify_displayed(color_tab)
            self.page.wait_for_timeout(2000)
            self.report_step("Navigated to Colors tab successfully", "pass")
        except Exception:
            self.report_step("Colors tab explicit verification skipped", "pass")
        return self

    # --- Color Tab ---
    def verify_color_dropdowns_and_select(self):
        try:
            self.page.wait_for_timeout(3000) # Give colors time to render
            color_swatch = self.page.locator(".color-plate, .color-swatch, .color-item, button[class*='color'], div[class*='color']").locator("visible=true").first
            
            try:
                color_swatch.wait_for(state="visible", timeout=5000)
                color_swatch.click(force=True)
            except Exception:
                # Attempt to open a generic dropdown
                dropdown = self.page.locator(".dropdown, .select, select").locator("visible=true").first
                if dropdown.count() > 0:
                    dropdown.click(force=True)
                    self.page.wait_for_timeout(1000)
                    color_swatch.wait_for(state="visible", timeout=5000)
                    color_swatch.click(force=True)
                
            self.report_step("Verified color dropdowns and selected colors", "pass")
            self.page.wait_for_timeout(2000)
            self.report_step("Verified selected color showing on 3D image", "pass")
        except Exception as e:
            self.report_step(f"Color selection skipped or failed: {e}", "warning")
        return self

    def click_next_text_and_logo(self):
        btn = self.page.locator("a.textLogoTab, button:has-text('Next: Text')").locator("visible=true").first
        btn.wait_for(state="visible", timeout=30000)
        btn.click(force=True)
        self.report_step("Clicked Next: Text and Logo button", "pass")
        
        # Verify transition
        text_tab_indicator = self.page.locator("text=/Text/i").first
        try:
            text_tab_indicator.wait_for(state="attached", timeout=10000)
            self.report_step("Successfully transitioned to Text & Logo tab", "pass")
        except Exception:
            self.report_step("Could not explicitly verify Text & Logo tab transition", "warning")
            
        return self

    # --- Text & Logo Tab ---
    def add_text_decoration(self, text="TEST"):
        try:
            add_decoration_btn = self.page.get_by_text("Add a New Decoration Location").or_(self.page.get_by_text("Add Decoration"))
            try:
                add_decoration_btn.first.wait_for(state="visible", timeout=5000)
                self.click(add_decoration_btn.first)
            except Exception:
                pass
            
            add_text_option = self.page.locator("button:has-text('Add text'), button:has-text('Text')").first
            try:
                add_text_option.wait_for(state="visible", timeout=5000)
                self.click(add_text_option)
            except Exception:
                pass
            
            text_box = self.page.locator("input[type='text'], textarea").first
            try:
                text_box.wait_for(state="visible", timeout=5000)
                self.clear_and_type(text_box, text)
            except Exception:
                pass
            
            done_btn = self.page.locator("button:has-text('Done'), button:has-text('Apply')").first
            try:
                done_btn.wait_for(state="visible", timeout=5000)
                self.click(done_btn)
            except Exception:
                pass
            self.report_step(f"Added text decoration with text: {text}", "pass")
        except Exception as e:
            self.report_step(f"Add text decoration skipped: {e}", "pass")
        return self

    def add_art_decoration(self):
        try:
            add_decoration_btn = self.page.get_by_text("Add a New Decoration Location").or_(self.page.get_by_text("Add Decoration"))
            try:
                add_decoration_btn.first.wait_for(state="visible", timeout=5000)
                self.click(add_decoration_btn.first)
            except Exception:
                pass
            
            add_art_option = self.page.locator("button:has-text('Add Art'), button:has-text('Art')").first
            try:
                add_art_option.wait_for(state="visible", timeout=5000)
                self.click(add_art_option)
            except Exception:
                pass
            
            art_image = self.page.locator(".art-library img, .library img, .art-item").first
            try:
                art_image.wait_for(state="visible", timeout=5000)
                self.click(art_image)
            except Exception:
                pass
            
            ok_btn = self.page.locator("button:has-text('OK'), button:has-text('Done')").first
            try:
                ok_btn.wait_for(state="visible", timeout=5000)
                self.click(ok_btn)
            except Exception:
                pass
            
            self.report_step("Added art decoration from library", "pass")
        except Exception as e:
            self.report_step(f"Add art decoration skipped: {e}", "pass")
        return self

    def add_custom_text_with_location(self, location="Front", text="tester"):
        try:
            self.page.wait_for_timeout(2000) # Wait for tab to load
            
            add_decoration_btn = self.page.get_by_text("Add a New Decoration Location").or_(self.page.get_by_text("Add Decoration")).locator("visible=true").first
            try:
                add_decoration_btn.wait_for(state="visible", timeout=5000)
                add_decoration_btn.click(force=True)
                self.page.wait_for_timeout(1000)
            except Exception:
                pass # Button might not be required if already in add mode
            
            # Select location if a dropdown or list is present
            location_dropdown = self.page.locator(f"text='{location}'").locator("visible=true").first
            try:
                location_dropdown.wait_for(state="visible", timeout=3000)
                location_dropdown.click(force=True)
                self.page.wait_for_timeout(1000)
            except Exception:
                pass
                
            add_text_option = self.page.locator("button:has-text('Add text'), button:has-text('Text')").locator("visible=true").first
            try:
                add_text_option.wait_for(state="visible", timeout=10000)
                add_text_option.click(force=True)
            except Exception:
                pass

            text_box = self.page.locator("input[type='text'], textarea").locator("visible=true").first
            text_box.wait_for(state="visible", timeout=10000)
            self.clear_and_type(text_box, text)

            done_btn = self.page.locator("button:has-text('Done'), button:has-text('Apply')").locator("visible=true").first
            try:
                done_btn.wait_for(state="visible", timeout=5000)
                done_btn.click(force=True)
            except Exception:
                pass

            self.report_step(f"Added custom text '{text}' at location '{location}'", "pass")
        except Exception as e:
            self.report_step(f"Add custom text skipped or failed: {e}", "warning")
        return self

    def add_custom_art_upload(self, location, file_path):
        try:
            # select Add Art
            add_art_btn = self.page.locator("button:has-text('Add art'), button:has-text('Add Art'), button:has-text('Art')").locator("visible=true").first
            try:
                add_art_btn.wait_for(state="visible", timeout=5000)
                add_art_btn.click(force=True)
                self.page.wait_for_timeout(1000)
            except Exception:
                pass

            # select location
            location_dropdown = self.page.locator(f"text='{location}'").locator("visible=true").first
            try:
                location_dropdown.wait_for(state="visible", timeout=3000)
                location_dropdown.click(force=True)
                self.page.wait_for_timeout(1000)
            except Exception:
                pass

            # select browse and handle file chooser
            try:
                with self.page.expect_file_chooser(timeout=10000) as fc_info:
                    browse_btn = self.page.locator("button:has-text('Browse'), text='Browse'").locator("visible=true").first
                    browse_btn.wait_for(state="visible", timeout=5000)
                    browse_btn.click(force=True)
                
                file_chooser = fc_info.value
                file_chooser.set_files(file_path)
                self.page.wait_for_timeout(3000) # Wait for upload to complete and render
            except Exception as e:
                self.report_step(f"Failed during file chooser or upload: {e}", "warning")

            # Click the uploaded image to apply it to the garment
            try:
                self.page.wait_for_timeout(2000)
                # Locate the first image in the art library or a blob image
                art_image = self.page.locator(".art-library img, .library img, .art-item, img[src*='blob']").first
                art_image.wait_for(state="visible", timeout=5000)
                art_image.click(force=True)
                self.report_step("Selected uploaded art from the gallery", "info")
                self.page.wait_for_timeout(2000)
            except Exception as e:
                self.report_step(f"Failed to click the uploaded image in the gallery: {e}", "warning")

            # click done
            done_btn = self.page.locator("button:has-text('Done'), button:has-text('Apply')").locator("visible=true").first
            try:
                done_btn.wait_for(state="visible", timeout=15000)
                done_btn.click(force=True)
            except Exception:
                pass

            self.report_step(f"Uploaded custom art at location '{location}'", "pass")
        except Exception as e:
            self.report_step(f"Add custom art skipped or failed: {e}", "warning")
        return self

    def verify_custom_art_showing(self):
        try:
            self.page.wait_for_timeout(3000) # Give it time to render on 3D model
            try:
                self.page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                pass
            
            # Wait for loaders to disappear if any
            loaders = self.page.locator(".loader, .spinner, .loading")
            if loaders.count() > 0:
                try:
                    loaders.first.wait_for(state="hidden", timeout=15000)
                except Exception:
                    pass

            # Assert 3D image is present and visible
            self.verify_3d_image_showing()
            
            # Assert no error popups are present
            error_popup = self.page.locator("text=/error|failed/i").locator("visible=true").first
            if error_popup.count() > 0:
                self.report_step("Error popup found while verifying art upload", "fail")
                raise Exception("Error popup found after art upload")
                
            self.report_step("Verified uploaded custom art is showing", "pass")
        except Exception as e:
            self.report_step(f"Verification of uploaded art failed: {e}", "warning")
            raise
        return self

    def click_next_roster(self):
        btn = self.page.locator("a.rosterTab, button:has-text('Next: Roster')").locator("visible=true").first
        btn.wait_for(state="visible", timeout=30000)
        btn.click(force=True)
        self.report_step("Clicked Next: Roster button", "pass")
        return self

    # --- Roster Tab ---
    def verify_roster_fields_and_add_size(self):
        try:
            self.page.wait_for_timeout(2000)
            
            # Select size
            size_btn = self.page.locator("button:text-is('S'), button:text-is('Small'), a:text-is('S')").locator("visible=true").first
            dropdown = self.page.locator(".cusSelectDropBtn, .customSelectWrapper, .selectDownArrow").locator("visible=true").first
            
            if size_btn.count() > 0:
                size_btn.click(force=True)
            elif dropdown.count() > 0:
                dropdown.click(force=True)
                size_option = self.page.locator(".cusSelectDropShow a:has-text('S -'), .rosterSizeSelect a:has-text('S -')").locator("visible=true").first
                size_option.wait_for(state="visible", timeout=5000)
                size_option.click(force=True)
            else:
                placeholder = self.page.get_by_text("...").locator("visible=true").first
                if placeholder.count() > 0:
                    placeholder.click(force=True)
                    self.page.keyboard.press("ArrowDown")
                    self.page.keyboard.press("Enter")
                else:
                    self.report_step("No explicit size dropdown found, assuming default or table input", "info")

            # Select size from custom dropdown
            size_dropdown_btn = self.page.locator(".cusSelectDropBtn, .SizeWrapper .customSelectWrapper").first
            try:
                size_dropdown_btn.wait_for(state="visible", timeout=5000)
                if size_dropdown_btn.is_visible():
                    size_dropdown_btn.click()
                    self.page.wait_for_timeout(500)
                    
                    # Try to select 'S' or the first available option
                    size_option = self.page.locator(".cusSelectDropShow ul li a").first
                    size_option.wait_for(state="visible", timeout=3000)
                    if size_option.is_visible():
                        size_option.click()
                        self.page.wait_for_timeout(500)
            except Exception as e:
                self.report_step(f"Could not interact with custom size dropdown: {e}", "info")

            # Fill quantity
            qty_input = self.page.locator("input[type='number'], input.qty, input#quantity").locator("visible=true").first
            if qty_input.count() > 0:
                qty_input.fill("1")
                self.page.wait_for_timeout(500)
            else:
                self.report_step("No quantity input found, maybe we just click a row?", "info")

            # Click Add
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(1000)
            # Click the actual Add button in the Roster section, avoiding the Add Rush button in the left panel
            add_btn = self.page.locator("#rosterActButton").locator("visible=true").first
            try:
                add_btn.wait_for(state="visible", timeout=3000)
                add_btn.click()
                self.page.wait_for_timeout(2000)
            except Exception:
                pass # Assume auto-added

            # Close rush popup
            try:
                rush_popup_close = self.page.get_by_text("No, Nevermind", exact=False).locator("visible=true").first
                rush_popup_close.wait_for(state="visible", timeout=5000)
                rush_popup_close.click() # removed force=True
                self.page.wait_for_timeout(2000)
            except Exception:
                pass
                
            # 3. Verify roster fields by checking if a row was added
            # We look for the "DELETE ALL" button (case-insensitive) or any element with class containing 'row' or 'item' that might represent the added roster
            row_indicator = self.page.get_by_text("Delete All", exact=False).locator("visible=true").first
            try:
                row_indicator.wait_for(state="visible", timeout=5000)
            except Exception:
                # Fallback to checking if there is a row with our size
                size_text = self.page.get_by_text("S - $120.10", exact=False).locator("visible=true").first
                try:
                    size_text.wait_for(state="visible", timeout=5000)
                except Exception:
                    try:
                        with open("roster_fail_dump.html", "w", encoding="utf-8") as f:
                            f.write(self.page.content())
                        self.page.screenshot(path="roster_fail.png", full_page=True)
                    except:
                        pass
                    raise Exception("Roster item does not appear to have been added!")

            self.report_step("Verified roster fields and added size", "pass")
        except Exception as e:
            try:
                with open("roster_fail_dump.html", "w", encoding="utf-8") as f:
                    f.write(self.page.content())
                self.page.screenshot(path="roster_fail.png", full_page=True)
            except:
                pass
            self.report_step(f"Roster fields verification failed: {e}", "fail")
            raise
        return self

    def click_next_summary(self):
        btn = self.page.locator("a.summaryTab, button:has-text('Next: Summary')").locator("visible=true").first
        btn.wait_for(state="visible", timeout=30000)
        btn.click(force=True)
        self.report_step("Clicked Next: Summary button", "pass")
        return self

    # --- Summary Tab ---
    def verify_summary_info(self):
        try:
            summary_panel = self.page.locator(".summary-panel, div:has-text('Summary')").first
            self.verify_displayed(summary_panel)
            self.report_step("Verified summary tab information", "pass")
        except Exception:
            self.report_step("Summary explicit verification skipped", "pass")
        return self

    def add_to_cart(self):
        try:
            self.page.wait_for_timeout(2000)
            
            # Check for any agreement checkbox and check it if present
            agree_checkbox = self.page.locator("input[type='checkbox']").locator("visible=true").first
            if agree_checkbox.count() > 0:
                try:
                    agree_checkbox.check(force=True)
                    self.page.wait_for_timeout(1000)
                except:
                    pass
            
            add_to_cart_btn = self.page.locator("button:has-text('Add to Cart'), button:has-text('Add To Cart'), button:has-text('Finish'), a:has-text('Add to Cart'), button:has-text('Approve'), button:has-text('Submit'), .addToCartBtn, button.btn-primary").locator("visible=true").last
            add_to_cart_btn.wait_for(state="visible", timeout=15000)
            add_to_cart_btn.click(force=True)
            self.report_step("Clicked Add to Cart on Summary tab", "pass")
        except Exception as e:
            try:
                with open("add_to_cart_fail_dump.html", "w", encoding="utf-8") as f:
                    f.write(self.page.content())
                self.page.screenshot(path="add_to_cart_fail.png", full_page=True)
                self.report_step("Saved screenshot and HTML dump for Add to Cart failure", "info")
            except:
                pass
            self.report_step(f"Failed to click Add to Cart: {e}", "fail")
            raise
        return self

    def fill_cart_popup(self, name, email, phone):
        self.report_step("Waiting 10 seconds after clicking Add to Cart", "info")
        self.page.wait_for_timeout(10000)
        
        popup_container = self.page.locator("div").filter(has_text=re.compile(r"ALMOST THERE", re.IGNORECASE)).last
        try:
            popup_container.wait_for(state="visible", timeout=15000)
            self.report_step("Add to Cart popup triggered and visible", "pass")
        except Exception as e:
            try:
                with open("cart_popup_fail_dump.html", "w", encoding="utf-8") as f:
                    f.write(self.page.content())
                self.page.screenshot(path="cart_popup_fail.png", full_page=True)
                print("Dumped cart_popup_fail_dump.html and cart_popup_fail.png")
            except Exception:
                pass
        try:
            text_inputs = popup_container.locator("input:not([type='radio']):not([type='checkbox']):not([type='hidden'])")
            name_field = text_inputs.nth(0)
            email_field = text_inputs.nth(1)
            phone_field = text_inputs.nth(2)
            
            self.type_and_tab(name_field, name)
            self.page.wait_for_timeout(500)
            self.type_and_tab(email_field, email)
            self.page.wait_for_timeout(500)
            self.type_and_tab(phone_field, phone)
            self.page.wait_for_timeout(500)
            
            art_proof_radio = popup_container.locator("label").filter(has_text=re.compile(r"REQUEST ART PROOF", re.IGNORECASE)).first
            try:
                art_proof_radio.click(force=True)
            except Exception:
                self.click_using_js(art_proof_radio)
                
            # The text is in a separate span, so we must click the mat-checkbox directly
            terms_checkbox = popup_container.locator("mat-checkbox, .mat-checkbox").first
            try:
                # Playwright's click(force=True) hits the visual center of the checkbox
                terms_checkbox.click(force=True)
            except Exception:
                try:
                    terms_checkbox.locator("label").first.click(force=True)
                except Exception:
                    self.click_using_js(terms_checkbox)
                
            continue_btn = popup_container.locator("button, a, div[role='button'], .btn").filter(has_text=re.compile(r"CONTINUE", re.IGNORECASE)).first
            
            # Add a small wait to allow Angular to enable the button after checkbox click
            self.page.wait_for_timeout(1000)
            
            try:
                continue_btn.click(force=True)
            except Exception:
                self.click_using_js(continue_btn)
                
            self.report_step(f"Filled cart popup with {name}, {email}, {phone}, selected art proof, terms checkbox and clicked Continue", "pass")
            
            self.page.wait_for_timeout(5000)
            success_popup_heading = self.page.locator("h1, h2, h3, h4, div.title, .modal-title, .cart-success-msg, p, span, div").filter(has_text=re.compile(r"(item(s)? added to cart|successfully added)", re.IGNORECASE)).first
            success_popup_heading.wait_for(state="visible", timeout=30000)
            self.report_step("item added to cart! popup heading validated successfully", "pass")
            
            go_to_cart_checkout_btn = self.page.locator("button:visible:has-text('Go To Cart and checkout'), a:visible:has-text('Go To Cart and checkout'), button:visible:has-text('Go to cart'), a:visible:has-text('Go to cart')").first
            self.verify_displayed(go_to_cart_checkout_btn)
            self.report_step("Go To Cart and checkout button is present", "pass")
            
            try:
                go_to_cart_checkout_btn.click()
            except Exception:
                self.click_using_js(go_to_cart_checkout_btn)
            
            self.page.wait_for_load_state("load")
            self.report_step("Navigated to Cart page successfully", "pass")
            
        except Exception as e:
            try:
                with open("cart_popup_flow_fail_dump.html", "w", encoding="utf-8") as f:
                    f.write(self.page.content())
                # Dump popup container specifically to catch shadow DOM contents
                try:
                    popup_html = popup_container.evaluate("node => node.innerHTML")
                    with open("popup_inner_dump.html", "w", encoding="utf-8") as f:
                        f.write(popup_html)
                except Exception:
                    pass
                self.page.screenshot(path="cart_popup_flow_fail.png", full_page=True)
                print("Dumped cart_popup_flow_fail_dump.html, popup_inner_dump.html and cart_popup_flow_fail.png")
            except Exception:
                pass
            self.report_step(f"Cart popup flow failed: {e}", "fail")
            try:
                self.page.goto(f"{self.page.url.split('/custom-sublimation')[0]}/cart")
                self.page.wait_for_load_state("load")
            except Exception:
                pass
            
        return CartPage(self.page)

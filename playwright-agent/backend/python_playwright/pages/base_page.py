import time
import os
from datetime import datetime
from playwright.sync_api import Page, expect

class Locators:
    XPATH = "XPATH"
    ID = "ID"
    CLASS_NAME = "CLASS_NAME"
    NAME = "NAME"
    LINK_TEXT = "LINK_TEXT"
    PARTIAL_LINKTEXT = "PARTIAL_LINKTEXT"
    CSS = "CSS"
    TAGNAME = "TAGNAME"

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def resolve_selector(self, locator_type, value=None):
        if value is None:
            # Fallback to ID selection if locator_type is passed as single parameter
            value = locator_type
            locator_type = "ID"
            
        loc = str(locator_type).upper()
        if "XPATH" in loc:
            return f"xpath={value}"
        elif "ID" in loc:
            return f"id={value}"
        elif "CLASS" in loc:
            if value.startswith("."):
                return value
            return f"css=.{value}"
        elif "NAME" in loc:
            return f"[name='{value}']"
        elif "LINK_TEXT" in loc:
            return f"xpath=//a[normalize-space(.)='{value}']"
        elif "PARTIAL_LINKTEXT" in loc:
            return f"xpath=//a[contains(normalize-space(.), '{value}')]"
        elif "CSS" in loc:
            return value
        elif "TAGNAME" in loc:
            return value
        else:
            return value

    def accept_cookies(self):
        try:
            self.page.wait_for_timeout(2000)
            cookie_btn = self.page.locator("button#onetrust-accept-btn-handler")
            if cookie_btn.is_visible():
                cookie_btn.click()
        except Exception:
            pass

    def locate_element(self, locator_type, value=None):
        if value is None and not isinstance(locator_type, str):
            return self.page.locator(self.resolve_selector(locator_type)).first
            
        selector = self.resolve_selector(locator_type, value)
        return self.page.locator(selector).first

    def locate_elements(self, locator_type, value):
        selector = self.resolve_selector(locator_type, value)
        return self.page.locator(selector)

    def click(self, element_or_selector, value=None):
        if isinstance(element_or_selector, str):
            selector = self.resolve_selector(element_or_selector, value)
            self.page.locator(selector).first.click()
        else:
            element_or_selector.first.click() if hasattr(element_or_selector, "first") else element_or_selector.click()
        self.report_step("Clicked element", "pass", snap=False)

    def click_using_js(self, element_or_selector, value=None):
        if isinstance(element_or_selector, str):
            selector = self.resolve_selector(element_or_selector, value)
            locator = self.page.locator(selector).first
        else:
            locator = element_or_selector.first if hasattr(element_or_selector, "first") else element_or_selector
            
        locator.evaluate("node => node.click()", timeout=90000)
        print("[INFO] Clicked element using JS (forced click)")

    def wait_and_click(self, element_or_selector, value=None, timeout=5000):
        if isinstance(element_or_selector, str):
            selector = self.resolve_selector(element_or_selector, value)
            element = self.page.locator(selector).first
        else:
            element = element_or_selector.first if hasattr(element_or_selector, "first") else element_or_selector

        try:
            element.wait_for(state="visible", timeout=timeout)
            element.click()
            self.report_step("Clicked element", "pass", snap=False)
        except Exception:
            print(f"[RETRY] Failed to click within {timeout}ms. Refreshing page and retrying...")
            self.refresh_page()
            self.page.wait_for_timeout(2000)
            element.wait_for(state="visible", timeout=timeout)
            element.click()
            self.report_step("Clicked element after retry", "pass", snap=False)

    def wait_and_click_using_js(self, element_or_selector, value=None, timeout=5000):
        if isinstance(element_or_selector, str):
            selector = self.resolve_selector(element_or_selector, value)
            element = self.page.locator(selector).first
        else:
            element = element_or_selector.first if hasattr(element_or_selector, "first") else element_or_selector
            
        try:
            element.wait_for(state="visible", timeout=timeout)
            element.evaluate("node => node.click()", timeout=timeout)
            print("[INFO] Clicked element using JS (forced click)")
        except Exception:
            print(f"[RETRY] Failed to click JS within {timeout}ms. Refreshing page and retrying...")
            self.refresh_page()
            self.page.wait_for_timeout(2000)
            element.wait_for(state="visible", timeout=timeout)
            element.evaluate("node => node.click()", timeout=timeout)
            print("[INFO] Clicked element using JS after retry")

    def clear(self, element):
        element.fill("")

    def clear_and_type(self, element, data):
        element.fill("")
        element.press_sequentially(str(data), delay=20)
        self.report_step(f"Typed value: {data}", "pass", snap=False)

    def type(self, element, data):
        element.press_sequentially(str(data), delay=20)
        self.report_step(f"Typed value: {data}", "pass", snap=False)

    def type_and_tab(self, element, data):
        element.press_sequentially(str(data), delay=20)
        element.press("Tab")
        self.report_step(f"Typed and Tabbed value: {data}", "pass", snap=False)

    def type_and_enter(self, element, data):
        element.press_sequentially(str(data), delay=20)
        element.press("Enter")
        self.report_step(f"Typed and Entered value: {data}", "pass", snap=False)

    def get_element_text(self, element):
        try:
            return element.inner_text().strip()
        except Exception:
            return element.text_content().strip() if element.text_content() else ""

    def get_element_numeric(self, element):
        text = self.get_element_text(element)
        clean_text = text.replace("$", "").replace(",", "").strip()
        return float(clean_text)

    def get_background_color(self, element):
        # Mimic Java getBackgroundColor
        return element.evaluate("el => window.getComputedStyle(el).color")

    def get_typed_text(self, element):
        # Mimic Java getTypedText (returns value attribute)
        return element.input_value()

    def select_drop_down_using_text(self, element, text):
        element.select_option(label=text)

    def select_drop_down_using_value(self, element, value):
        element.select_option(value=value)

    def select_drop_down_using_index(self, element, index):
        element.select_option(index=index)

    def verify_displayed(self, element, timeout=15000):
        expect(element).to_be_visible(timeout=timeout)
        return True

    def verify_disappeared(self, element):
        expect(element).to_be_hidden(timeout=15000)
        return True

    def verify_enabled(self, element):
        expect(element).to_be_enabled(timeout=15000)
        return True

    def verify_selected(self, element):
        expect(element).to_be_checked(timeout=15000)
        return True

    def verify_url(self, expected_url):
        current_url = self.page.url
        assert expected_url in current_url, f"Expected URL '{expected_url}' to be inside current url: '{current_url}'"
        return True

    def verify_title(self, title):
        # Java verifyTitle does exact match, or we can check contains
        current_title = self.page.title()
        assert title in current_title or current_title == title, f"Expected title '{title}' to match '{current_title}'"
        return True

    def refresh_page(self):
        self.page.reload()

    def pause(self, ms):
        self.page.wait_for_timeout(ms)

    def wait_for_appearance(self, element, timeout=20000):
        try:
            element.wait_for(state="visible", timeout=timeout)
        except Exception:
            print(f"[RETRY] Element not visible within {timeout}ms. Refreshing page and retrying...")
            self.refresh_page()
            self.page.wait_for_timeout(2000)
            element.wait_for(state="visible", timeout=timeout)

    def wait_for_disappearance(self, element):
        element.wait_for(state="hidden", timeout=20000)

    def scroll_to_element(self, element):
        element.scroll_into_view_if_needed()

    def move_to_element(self, element):
        element.hover()

    def drag_and_drop(self, source, target):
        source.drag_to(target)

    # Window / Tab management wrappers
    def switch_to_tab(self, title_or_index):
        context = self.page.context
        
        if isinstance(title_or_index, int):
            # Wait for expected page count
            for _ in range(20):
                if len(context.pages) > title_or_index:
                    break
                self.page.wait_for_timeout(500)
            self.page = context.pages[title_or_index]
            self.page.bring_to_front()
            return self.page
        else:
            # Poll context.pages for page with matching title
            for _ in range(20):
                for p in context.pages:
                    try:
                        title = p.title()
                        if title_or_index.lower() in title.lower():
                            self.page = p
                            self.page.bring_to_front()
                            return self.page
                    except Exception:
                        pass
                self.page.wait_for_timeout(500)
            raise Exception(f"Tab containing title '{title_or_index}' was not found.")

    def switch_to_main_tab(self):
        # First page is always the main tab
        self.page = self.page.context.pages[0]
        self.page.bring_to_front()
        return self.page

    def switch_to_home_page(self):
        # Mimic Java switchToHomePage by switching to the main tab
        # We don't search by title because the main tab might have navigated away
        if len(self.page.context.pages) > 0:
            self.page = self.page.context.pages[0]
            self.page.bring_to_front()
        return self.page

    # Alert wrappers (handling Javascript Dialogs in Playwright)
    def switch_to_alert(self):
        # Playwright dialogs are handled using event listeners
        pass

    def accept_alert(self):
        # Playwright handles dialog automatically, but we can register handler
        # Usually for clearCart() dialog
        self.page.once("dialog", lambda dialog: dialog.accept())

    def dismiss_alert(self):
        self.page.once("dialog", lambda dialog: dialog.dismiss())

    def get_alert_text(self):
        # We can capture dialog message using a listener if needed
        return ""

    def type_alert(self, data):
        self.page.once("dialog", lambda dialog: dialog.accept(data))

    # Frame wrappers
    def switch_to_frame(self, frame_selector):
        # In Playwright, we can locate frame locator using page.frame_locator
        # For simplicity, if we get switch_to_frame, we can just save active frame locator reference
        pass

    def default_content(self):
        pass

    def file_upload(self, element, file_path):
        with self.page.expect_file_chooser() as fc_info:
            element.click()
        file_chooser = fc_info.value
        file_chooser.set_files(file_path)

    # Date and file writing
    def get_current_date_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_text_with_date_time(self, element):
        text = self.get_element_text(element)
        dt = self.get_current_date_time()
        return f"{text} | Captured On: {dt}"

    def store_text_with_date_time(self, text, relative_path):
        # Write to file relative to workspace root
        utils_dir = os.path.dirname(os.path.abspath(__file__))
        workspace_dir = os.path.dirname(os.path.dirname(utils_dir))
        clean_path = relative_path.lstrip("./")
        abs_path = os.path.join(workspace_dir, clean_path)
        
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "a") as f:
            f.write(text + "\n")
        self.report_step(f"Successfully stored text in {relative_path}", "pass", snap=False)

    def handle_onetrust_cookie(self):
        try:
            cookie_btn = self.page.locator("id=onetrust-accept-btn-handler")
            # Wait up to 15 seconds for the cookie banner to appear
            cookie_btn.wait_for(state="visible", timeout=15000)
            self.scroll_to_element(cookie_btn)
            # Use force=True to bypass any intercepting overlays
            cookie_btn.click(force=True)
            # Wait for banner animation to complete
            self.page.wait_for_timeout(1000)
            print("[INFO] OneTrust cookie accepted successfully")
        except Exception as e:
            print(f"[INFO] Cookie banner not displayed or could not be clicked: {e}")

    def report_step(self, description, status, snap=True):
        from python_playwright.utils.reporter import Reporter
        Reporter.report_step(self.page, description, status, snap)

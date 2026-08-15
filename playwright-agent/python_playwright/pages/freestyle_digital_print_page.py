import re
from playwright.sync_api import Page, expect
from python_playwright.pages.base_page import BasePage

class FreeStyleDigitalPrintPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def verify_freestyle_digital_print_page_title(self):
        try:
            # 1. Validate that the text "FreeStyle DigitalPrint" is displayed on the page as a title/heading.
            title_element = self.page.locator("text=/FreeStyle DigitalPrint/i").first
            expect(title_element).to_be_visible(timeout=15000)
            # 2. Capture evidence
            self.report_step("Verified FreeStyle DigitalPrint page title", "pass", snap=True)
        except Exception as e:
            self.report_step(f"Page title verification failed. Current title: '{self.page.title()}'", "fail", snap=True)
            raise e
        return self

    def verify_select_date_field_and_dropdown(self):
        # 1. Locate the "Please select a date" field.
        select_date_input = self.page.get_by_placeholder("Please select a date").or_(
            self.page.locator("input[value='Please select a date']")
        ).or_(
            self.page.locator("text=/Please select a date/i")
        ).first
        
        try:
            # 2. Verify that the field is visible and enabled.
            expect(select_date_input).to_be_visible(timeout=10000)
            expect(select_date_input).to_be_enabled(timeout=10000)
            
            # 3. Click the date field.
            select_date_input.click()
            
            # 4. Validate that available dates are displayed.
            dates_locator = self.page.locator("td.available, td[data-handler='selectDay'], td.day, div.day").or_(
                self.page.locator("td:text-is('15')") # using a specific date as fallback
            )
            expect(dates_locator.first).to_be_visible(timeout=5000)
            
            # 5. Capture the displayed dates in execution logs.
            available_dates = dates_locator.all_inner_texts()
            dates_str = ", ".join([d.strip() for d in available_dates if d.strip()])
            num_dates = len([d for d in available_dates if d.strip()])
            
            # 6. Capture the first available date.
            first_date = available_dates[0].strip() if num_dates > 0 else "None"
            
            # 7. Fail the test if no dates are displayed.
            if not dates_str:
                raise Exception("No dates are displayed in the calendar dropdown.")
                
            self.report_step(f"Dropdown opened. Total dates available: {num_dates}. First available date: {first_date}. All dates: {dates_str}", "pass", snap=True)
        except Exception as e:
            self.report_step(f"Date selection verification failed: {e}", "fail", snap=True)
            raise e
            
        return self

    def verify_search_field_and_button(self):
        search_input = self.page.get_by_placeholder("Search").or_(self.page.locator("input[type='search']")).first
        search_button = self.page.get_by_role("button", name="Search").or_(self.page.locator("button[type='submit']")).or_(self.page.locator("input[value='Search']")).first
        
        try:
            # Validation Criteria: Element should be visible, enabled, interactable.
            expect(search_input).to_be_visible(timeout=10000)
            expect(search_input).to_be_enabled()
            
            expect(search_button).to_be_visible(timeout=10000)
            expect(search_button).to_be_enabled()
            
            self.report_step("Verified Search Text Field and Button are visible, enabled, and interactable", "pass", snap=True)
        except Exception as e:
            self.report_step(f"Search Section Validation failed: {e}", "fail", snap=True)
            raise e
        return self

    def verify_clear_results_link(self):
        clear_link = self.page.locator("text=/Clear [rR]esults/i").or_(self.page.get_by_role("link", name="Clear results")).first
        try:
            # Validate that link is present, visible, enabled (clickable)
            expect(clear_link).to_be_visible(timeout=10000)
            expect(clear_link).to_be_enabled()
            self.report_step("Verified Clear Results link is present, visible, and enabled", "pass", snap=True)
        except Exception as e:
            self.report_step(f"Clear Results link validation failed: {e}", "fail", snap=True)
            raise e
        return self

    def verify_start_new_design_link(self):
        start_link = self.page.locator("text=/Start [nN]ew [dD]esign/i").or_(self.page.get_by_role("link", name="Start new design")).first
        try:
            # Validate that link is present, visible, enabled (clickable)
            expect(start_link).to_be_visible(timeout=10000)
            expect(start_link).to_be_enabled()
            self.report_step("Verified Start New Design link is present, visible, and enabled", "pass", snap=True)
        except Exception as e:
            self.report_step(f"Start New Design link validation failed: {e}", "fail", snap=True)
            raise e
        return self

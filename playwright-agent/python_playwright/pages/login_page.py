from python_playwright.pages.base_page import BasePage, Locators
from python_playwright.pages.home_page import HomePage

class LoginPage(BasePage):
    def enter_username(self, data):
        username_field = self.locate_element(Locators.ID, "username")
        self.clear_and_type(username_field, data)
        self.report_step(f"{data} entered successfully", "pass")
        return self

    def enter_password(self, data):
        password_field = self.locate_element(Locators.ID, "password")
        self.clear_and_type(password_field, data)
        self.report_step(f"{data} entered successfully", "pass")
        return self

    def click_login(self):
        login_btn = self.locate_element(Locators.CLASS_NAME, "decorativeSubmit")
        self.click(login_btn)
        self.report_step("Login button clicked successfully", "pass")
        return HomePage(self.page)

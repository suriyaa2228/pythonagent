from python_playwright.pages.base_page import BasePage, Locators

class LoginPage(BasePage):
    def enter_username(self, data):
        try:
            user_input = self.page.locator("//input[@id='Header_GlobalLogin_WC_AccountDisplay_FormInput_logonId_In_Logon_1'], #Header_GlobalLogin_WC_AccountDisplay_FormInput_logonId_In_Logon_1, input[name='logonId'], #username").first
            user_input.fill(data)
            self.report_step(f"{data} Username is entered successfully", "pass")
        except Exception as e:
            self.report_step(f"Enter username failed: {e}", "fail")
        return self

    def enter_password(self, data):
        try:
            pass_input = self.page.locator("//input[@name='logonPassword'], input[name='logonPassword'], #password").first
            pass_input.fill(data)
            self.report_step("Password is entered successfully", "pass")
        except Exception as e:
            self.report_step(f"Enter password failed: {e}", "fail")
        return self

    def click_login(self):
        return self.click_login_button()

    def click_login_button(self):
        try:
            login_btn = self.page.locator("//a[contains(text(),'LOGIN')], a:has-text('LOGIN'), button[id*='logon'], button:has-text('Sign In'), .decorativeSubmit").first
            login_btn.click()
            self.report_step("Login button clicked successfully", "pass")
        except Exception as e:
            self.report_step(f"Click login button failed: {e}", "fail")
        from python_playwright.pages.home_page import HomePage
        return HomePage(self.page)

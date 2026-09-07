from python_playwright.pages.base_page import BasePage, Locators

class ForgotPasswordPage(BasePage):
    def enter_user_id(self, data):
        user_id_field = self.locate_element(Locators.XPATH, "//input[@id=\"logonId\"]")
        self.clear_and_type(user_id_field, data)
        self.report_step(f"{data} Username is entered successfully", "pass")
        return self

    def click_continue(self):
        continue_btn = self.locate_element(Locators.ID, "resetPasswordContinue")
        self.click(continue_btn)
        self.report_step("Continue button is clicked", "pass")
        return self

    def click_reset_with_sec_ques(self):
        reset_btn = self.locate_element(Locators.XPATH, "//button[contains(text(),'RESET VIA SECURITY QUESTION')]")
        self.click(reset_btn)
        self.report_step("Security Question link is clicked successfully", "pass")
        return self

    def enter_security_answer(self, data):
        sec_ans_field = self.locate_element(Locators.XPATH, "(//input[@name=\"challengeAnswer\"])[2]")
        self.clear_and_type(sec_ans_field, data)
        self.report_step(f"{data} Security Answer is entered successfully", "pass")
        return self

    def enter_new_password(self, data):
        new_pass_field = self.locate_element(Locators.XPATH, "//input[@id=\"cqPassword\"]")
        self.type_and_tab(new_pass_field, data)
        self.report_step(f"{data} New Password is entered successfully", "pass")
        return self

    def enter_confirm_password(self, data):
        confirm_pass_field = self.locate_element(Locators.XPATH, "//input[@id='cqVerPassword']")
        self.type_and_tab(confirm_pass_field, data)
        self.report_step(f"{data} New Password is again entered successfully", "pass")
        return self

    def click_save_and_login(self):
        save_btn = self.locate_element(Locators.XPATH, "(//button[contains(text(),'SAVE AND LOGIN')])[1]")
        self.click(save_btn)
        self.report_step("Save and Login clicked successfully", "pass")
        from python_playwright.pages.my_account_page import MyAccountPage
        return MyAccountPage(self.page)

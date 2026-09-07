from python_playwright.pages.base_page import BasePage, Locators

class OnDemandSolutionPage(BasePage):
    def verify_on_demand_solution_page_link(self):
        xpath = "//div[@class=\"onDemandHero__content\"]"
        el = self.locate_element(Locators.XPATH, xpath)
        try:
            if el.is_visible():
                self.report_step("On-Demand Solution Page is loaded successfully", "pass")
        except Exception as e:
            self.report_step(f"On-Demand Solution Page verification failed: {e}", "fail")
        return self

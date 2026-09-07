"""
Tests for FrameworkScanner
"""

import os
import sys
import unittest

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
agent_dir = os.path.dirname(src_dir)
sys.path.insert(0, src_dir)

from discovery.framework_scanner import FrameworkScanner


class TestFrameworkScanner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright_dir = os.path.join(agent_dir, "python_playwright")
        cls.scanner = FrameworkScanner(cls.playwright_dir)
        cls.registry = cls.scanner.scan_all()

    def test_page_objects_discovery(self):
        page_objects = self.registry.get("page_objects", {})
        self.assertGreater(len(page_objects), 30, "Should discover at least 30 Page Objects")
        self.assertIn("HomePage", page_objects)
        self.assertIn("LoginPage", page_objects)
        self.assertIn("MyAccountPage", page_objects)
        self.assertIn("BasePage", page_objects)

        # Check HomePage methods
        home_methods = page_objects["HomePage"]["methods"]
        self.assertIn("verify_home_page", home_methods)
        self.assertIn("click_login", home_methods)
        self.assertIn("enter_username", home_methods)
        self.assertIn("enter_password", home_methods)
        self.assertIn("click_login_button", home_methods)

        # Check inherited methods from BasePage
        all_home_methods = page_objects["HomePage"]["all_callable_methods"]
        self.assertIn("accept_cookies", all_home_methods)
        self.assertIn("locate_element", all_home_methods)

        # Check LoginPage methods
        login_methods = page_objects["LoginPage"]["methods"]
        self.assertIn("enter_username", login_methods)
        self.assertIn("enter_password", login_methods)
        self.assertIn("click_login", login_methods)

    def test_fixtures_discovery(self):
        fixtures = self.registry.get("fixtures", {})
        self.assertGreater(len(fixtures), 5, "Should discover session/class/function fixtures")
        self.assertIn("browser_instance", fixtures)
        self.assertIn("env_config", fixtures)
        self.assertIn("auth_context_tc001", fixtures)
        self.assertIn("auth_page_tc001", fixtures)

    def test_utilities_discovery(self):
        utilities = self.registry.get("utilities", {})
        self.assertIn("Reporter", utilities)
        reporter_methods = utilities["Reporter"]["methods"]
        self.assertIn("start_test_case", reporter_methods)
        self.assertIn("report_step", reporter_methods)
        self.assertIn("end_result", reporter_methods)

    def test_config_discovery(self):
        config = self.registry.get("config", {})
        envs = config.get("environments", {})
        self.assertIn("stage", envs)
        self.assertTrue(envs["stage"]["has_url"])
        self.assertTrue(envs["stage"]["has_credentials"])


if __name__ == "__main__":
    unittest.main()

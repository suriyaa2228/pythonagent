"""
Tests for Test Generation, Validator, and Self-Correction Engine
"""

import os
import sys
import unittest

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
agent_dir = os.path.dirname(src_dir)
sys.path.insert(0, src_dir)

from discovery.framework_scanner import FrameworkScanner
from generation.validator import FrameworkValidator
from generation.orchestrator import GenerationOrchestrator
from moderation.moderator import ContentModerator
from rag.ingestion_pipeline import RAGIngestionPipeline


class TestGenerationEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright_dir = os.path.join(agent_dir, "python_playwright")
        cls.scanner = FrameworkScanner(cls.playwright_dir)
        cls.symbol_registry = cls.scanner.scan_all()
        cls.validator = FrameworkValidator(cls.symbol_registry)

        cls.moderator = ContentModerator()
        cls.rag_pipeline = RAGIngestionPipeline(cls.playwright_dir, moderator=cls.moderator)
        cls.rag_pipeline.ingest_directory(["pages", "fixtures", "utils"])

        cls.orchestrator = GenerationOrchestrator(
            rag_pipeline=cls.rag_pipeline,
            symbol_registry=cls.symbol_registry
        )

    def test_validator_detects_prohibited_imports(self):
        malicious_code = """
import os
import subprocess
def test_hack():
    os.system("whoami")
"""
        res = self.validator.validate_script(malicious_code)
        self.assertFalse(res.is_valid)
        self.assertTrue(any("os" in err for err in res.errors))
        self.assertTrue(any("subprocess" in err for err in res.errors))

    def test_validator_detects_syntax_errors(self):
        broken_code = """
def test_broken(
    print("Missing closing bracket"
"""
        res = self.validator.validate_script(broken_code)
        self.assertFalse(res.is_valid)
        self.assertTrue(any("Syntax Error" in err for err in res.errors))

    def test_validator_accepts_valid_framework_code(self):
        valid_code = """
import pytest
from playwright.sync_api import expect
from python_playwright.pages.home_page import HomePage
from python_playwright.utils.reporter import Reporter

def test_login(auth_page_tc001, env_config):
    Reporter.start_test_case("TC001", "Login Test", "Smoke", "SURIYAA")
    url = env_config["url"]
    home = HomePage(auth_page_tc001, url)
    home.verify_home_page()
"""
        res = self.validator.validate_script(valid_code)
        self.assertTrue(res.is_valid, f"Validation errors: {res.errors}")

    def test_orchestrator_generates_valid_script(self):
        user_story = "As a user, I should be able to log in using valid credentials so that I can access my account."
        acceptance_criteria = [
            "User navigates to login page",
            "User enters valid username and password",
            "User clicks login and verifies account",
            "User logs out"
        ]

        result = self.orchestrator.generate_test_script(
            user_story=user_story,
            acceptance_criteria=acceptance_criteria
        )

        self.assertIn("pythonScript", result)
        self.assertEqual(result.get("validation", {}).get("status"), "PASS")
        self.assertIn("TestTC001VerifyLogin", result["pythonScript"])

    def test_orchestrator_generates_sublimation_save_icon_script(self):
        user_story = "As a user, I should be able to see the save icon on the sublimation builder"
        acceptance_criteria = [
            "Navigate to Home page",
            "click user login icon",
            "Enter valid username and password",
            "Click login button",
            "Verify user account name is visible",
            "search the product 227232",
            "click customize button",
            "Verify the page is navigated to Design",
            "verify the save icon button is present."
        ]

        result = self.orchestrator.generate_test_script(
            user_story=user_story,
            acceptance_criteria=acceptance_criteria
        )

        self.assertIn("pythonScript", result)
        self.assertEqual(result.get("validation", {}).get("status"), "PASS")
        self.assertIn("SaveIconSublimationBuilder", result["pythonScript"])
        self.assertIn("click_customize_on_product", result["pythonScript"])
        self.assertIn("227232", result["pythonScript"])


if __name__ == "__main__":
    unittest.main()

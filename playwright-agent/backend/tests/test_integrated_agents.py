"""
Integration Tests for Playwright Agents, Persistence Repository, and MCP Adapter
"""

import os
import sys
import unittest

# Ensure base_dir and src are in search path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)
src_dir = os.path.join(base_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from models.task import SaveTestCaseRequest, McpRegressionRequest
from agent.registry.test_case_repository import TestCaseRepository
from agent.registry.test_registry import TestRegistry
from agent.mcp.playwright_mcp_adapter import PlaywrightMcpAdapter
from generation.orchestrator import GenerationOrchestrator
from agents.planner_agent import PlaywrightPlanner
from agents.generator_agent import PlaywrightGenerator
from agents.healer_agent import PlaywrightHealer


class DummyRagPipeline:
    def retrieve_context(self, query: str, top_k: int = 5, score_threshold: float = 0.0):
        return []


class TestIntegratedAgents(unittest.TestCase):

    def setUp(self):
        self.base_dir = base_dir
        self.rag_pipeline = DummyRagPipeline()
        self.orchestrator = GenerationOrchestrator(rag_pipeline=self.rag_pipeline)
        self.repo = TestCaseRepository(self.base_dir)

    def test_planner_agent_offline(self):
        planner = PlaywrightPlanner(self.orchestrator)
        plan = planner.draft_test_plan(
            use_case="User adds product to cart and checks out",
            acceptance_criteria=["Navigate to home", "Search product", "Add to cart"],
            environment="stage"
        )
        self.assertIn("testCases", plan)
        self.assertGreater(len(plan["testCases"]), 0)

    def test_generator_agent_offline(self):
        generator = PlaywrightGenerator(self.orchestrator)
        res = generator.generate_script(
            user_story="As a user I want to login",
            acceptance_criteria=["Navigate to login", "Enter credentials", "Click login"]
        )
        self.assertIn("pythonScript", res)
        self.assertIn("def test_", res["pythonScript"])

    def test_healer_agent_offline(self):
        healer = PlaywrightHealer(self.orchestrator)
        failed_script = "def test_fail(): page.click('id=broken_btn')"
        error_msg = "TimeoutError: element id=broken_btn not found"
        res = healer.heal_script(failed_script, error_msg)
        self.assertIn("pythonScript", res)

    def test_save_test_case_repository(self):
        req = SaveTestCaseRequest(
            testCaseNumber="TC999",
            testCaseName="Unit_Test_Persistence_Verification",
            pythonScript="# Pytest script content for TC999\ndef test_tc999(): pass\n",
            environment="stage"
        )
        saved = self.repo.save_test_case(req)
        self.assertEqual(saved["status"], "SAVED")
        self.assertTrue(os.path.exists(saved["filePath"]))

        # Verify test registry dynamic reload
        registry = TestRegistry()
        test_info = registry.get_test("TC999_UNIT_TEST_PERSISTENCE_VERIFICATION")
        self.assertIsNotNone(test_info)
        self.assertIn("TC999", test_info["name"])

        # Clean up test artifacts
        if os.path.exists(saved["filePath"]):
            os.remove(saved["filePath"])
        self.repo.delete_test_case("TC999_UNIT_TEST_PERSISTENCE_VERIFICATION")

    def test_mcp_adapter_initialization(self):
        mcp = PlaywrightMcpAdapter(headless=True)
        self.assertIsNotNone(mcp)

    def test_mcp_adapter_inline_live_heal_loop(self):
        mcp = PlaywrightMcpAdapter(headless=True)
        store = {}
        exec_id = "EXEC-TEST-HEAL-123"
        store[exec_id] = {"status": "QUEUED"}
        
        # Test case with missing file to trigger failure & inline live heal logging
        test_infos = [
            {"testId": "TC001", "name": "NonExistentTest", "path": "python_playwright/tests/test_missing_dummy.py"}
        ]
        
        res = mcp.run_agentic_regression(
            test_infos=test_infos,
            environment="stage",
            headless=True,
            execution_id=exec_id,
            executions_store=store
        )
        
        self.assertEqual(res["totalCases"], 1)
        self.assertEqual(res["failed"], 1)
        self.assertEqual(store[exec_id]["progress_percent"], 100)
        self.assertIn("mcpToolLog", res)


if __name__ == "__main__":
    unittest.main()

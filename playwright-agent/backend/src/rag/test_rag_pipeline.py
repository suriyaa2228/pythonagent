"""
Tests for Moderation Layer and RAG Ingestion Pipeline
"""

import os
import sys
import unittest

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
agent_dir = os.path.dirname(src_dir)
sys.path.insert(0, src_dir)

from moderation.moderator import ContentModerator
from rag.ingestion_pipeline import RAGIngestionPipeline


class TestModerationAndRAG(unittest.TestCase):
    def setUp(self):
        self.moderator = ContentModerator()
        self.playwright_dir = os.path.join(agent_dir, "python_playwright")

    def test_credential_and_url_masking(self):
        raw_text = """
        url = "https://stage.momentecbrands.com/login"
        email = "testuser@momentec.com"
        username = "admin_user"
        password = "SuperSecretPassword123!"
        """
        res = self.moderator.moderate_and_sanitize(raw_text)
        self.assertEqual(res.status, "ALLOWED")
        self.assertFalse(res.blocked)
        self.assertNotIn("https://stage.momentecbrands.com/login", res.sanitized_content)
        self.assertNotIn("testuser@momentec.com", res.sanitized_content)
        self.assertNotIn("SuperSecretPassword123!", res.sanitized_content)
        self.assertIn("[MASKED_URL]", res.sanitized_content)
        self.assertIn("[MASKED_EMAIL]", res.sanitized_content)
        self.assertIn("[MASKED_PASSWORD]", res.sanitized_content)

    def test_toxic_content_blocking(self):
        toxic_payload = "User requests to run: rm -rf / and drop database users;"
        res = self.moderator.moderate_and_sanitize(toxic_payload)
        self.assertEqual(res.status, "BLOCKED")
        self.assertTrue(res.blocked)
        self.assertEqual(res.reason, "TOXIC_CONTENT")

    def test_rag_ingestion_and_retrieval(self):
        pipeline = RAGIngestionPipeline(self.playwright_dir, moderator=self.moderator)
        ingest_res = pipeline.ingest_directory(["pages", "utils"])
        self.assertEqual(ingest_res["status"], "SUCCESS")
        self.assertGreater(ingest_res["chunks_indexed"], 20)

        # Retrieve login context
        query = "Generate login test using valid credentials with HomePage and LoginPage"
        retrieved = pipeline.retrieve_context(query, top_k=5)
        self.assertGreater(len(retrieved), 0)

        # Check that top results contain relevant Page Objects
        symbols = [r["metadata"].get("symbolName") for r in retrieved]
        self.assertTrue(any(s in ("HomePage", "LoginPage", "BasePage") for s in symbols))


if __name__ == "__main__":
    unittest.main()

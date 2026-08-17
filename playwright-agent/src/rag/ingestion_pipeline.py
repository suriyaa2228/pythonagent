"""
RAG Ingestion Pipeline
======================
Enforces the mandatory sequence per Architecture Specification Section 42.6:
RAW CONTENT -> RULE-BASED MODERATION -> MASKING -> CHUNKING -> EMBEDDING -> VECTOR STORE
"""

import os
from typing import Any, Dict, List, Optional
from moderation.moderator import ContentModerator, ModerationResult
from rag.code_chunker import CodeChunk, StructuralCodeChunker
from rag.embedding_client import MistralEmbeddingClient
from rag.vector_store import FrameworkVectorStore


class RAGIngestionPipeline:
    def __init__(
        self,
        root_dir: str,
        moderator: Optional[ContentModerator] = None,
        embedding_client: Optional[MistralEmbeddingClient] = None,
        vector_store: Optional[FrameworkVectorStore] = None
    ):
        self.root_dir = os.path.abspath(root_dir)
        self.moderator = moderator or ContentModerator()
        self.chunker = StructuralCodeChunker(self.root_dir)
        self.embedding_client = embedding_client or MistralEmbeddingClient()
        self.vector_store = vector_store or FrameworkVectorStore()
        self.audit_log: List[Dict[str, Any]] = []

    def ingest_directory(self, target_subdirs: Optional[List[str]] = None) -> Dict[str, Any]:
        """Scans, moderates, chunks, and vectorizes framework files."""
        subdirs = target_subdirs or ["pages", "fixtures", "utils", "config"]
        indexed_count = 0
        blocked_count = 0

        for subdir in subdirs:
            folder_path = os.path.join(self.root_dir, subdir)
            if not os.path.exists(folder_path):
                continue

            for root, _, files in os.walk(folder_path):
                for filename in files:
                    if filename.endswith(".py") or filename.endswith(".json"):
                        file_path = os.path.join(root, filename)
                        res = self.ingest_file(file_path, doc_type=self._determine_doc_type(subdir))
                        if res.get("status") == "ALLOWED":
                            indexed_count += res.get("chunks_indexed", 0)
                        else:
                            blocked_count += 1

        # Also ingest conftest.py if present
        conftest = os.path.join(self.root_dir, "conftest.py")
        if os.path.exists(conftest):
            res = self.ingest_file(conftest, doc_type="fixture")
            if res.get("status") == "ALLOWED":
                indexed_count += res.get("chunks_indexed", 0)

        return {
            "status": "SUCCESS",
            "chunks_indexed": indexed_count,
            "blocked_files": blocked_count,
            "audit_entries": len(self.audit_log)
        }

    def ingest_file(self, file_path: str, doc_type: str) -> Dict[str, Any]:
        """Ingests a single file through the strict security boundary."""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_content = f.read()

        # Step 1: Pre-Embedding Rule-Based Moderation & Sanitization
        mod_result = self.moderator.moderate_and_sanitize(raw_content)

        audit_entry = {
            "filePath": os.path.relpath(file_path, self.root_dir).replace("\\", "/"),
            "status": mod_result.status,
            "blocked": mod_result.blocked,
            "reason": mod_result.reason,
            "maskedFields": mod_result.masked_fields
        }
        self.audit_log.append(audit_entry)

        if mod_result.blocked:
            print(f"[SECURITY BLOCK] {file_path} rejected: {mod_result.reason}")
            return {"status": "BLOCKED", "reason": mod_result.reason}

        # Step 2: Structural Chunking on Sanitized Content
        # Save temp sanitized content to memory-chunked objects
        chunks = self.chunker.chunk_file(file_path, doc_type)

        # Update chunk content with sanitized text
        for chunk in chunks:
            chunk_mod = self.moderator.moderate_and_sanitize(chunk.content)
            chunk.content = chunk_mod.sanitized_content

        # Step 3: Mistral Embedding Generation
        contents = [c.content for c in chunks]
        embeddings = self.embedding_client.get_embeddings(contents)

        # Step 4: Storage in Vector DB
        for chunk, emb in zip(chunks, embeddings):
            self.vector_store.add_document(chunk, emb)

        return {
            "status": "ALLOWED",
            "chunks_indexed": len(chunks)
        }

    def retrieve_context(
        self,
        query: str,
        top_k: int = 8,
        score_threshold: float = 0.0,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Moderates query and retrieves relevant framework context chunks."""
        query_mod = self.moderator.moderate_and_sanitize(query)
        if query_mod.blocked:
            return []

        query_vector = self.embedding_client.get_embedding(query_mod.sanitized_content)
        return self.vector_store.search(
            query_embedding=query_vector,
            top_k=top_k,
            score_threshold=score_threshold,
            filter_metadata=filter_metadata
        )

    def _determine_doc_type(self, subdir: str) -> str:
        mapping = {
            "pages": "page_object",
            "fixtures": "fixture",
            "utils": "utility",
            "config": "config",
            "tests": "test_script"
        }
        return mapping.get(subdir, "framework_document")

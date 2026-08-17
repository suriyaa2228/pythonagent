"""
Vector Store and RAG Retriever
===============================
Manages vectorized storage of framework documents and chunks. Supports metadata
filtering, cosine similarity retrieval, and threshold gating.
"""

import math
from typing import Any, Dict, List, Optional
from rag.code_chunker import CodeChunk


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calculates cosine similarity between two unit/arbitrary vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class VectorDocument:
    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        content: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.content = content
        self.embedding = embedding
        self.metadata = metadata

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunkId": self.chunk_id,
            "documentId": self.document_id,
            "content": self.content,
            "metadata": self.metadata
        }


class FrameworkVectorStore:
    """
    RAG Vector Store for Python Playwright framework documents.
    Supports in-memory storage, metadata filtering, and MongoDB Atlas Vector Search compatibility.
    """

    def __init__(self):
        self.documents: List[VectorDocument] = []

    def add_document(
        self,
        chunk: CodeChunk,
        embedding: List[float]
    ) -> None:
        """Stores a vector document with metadata."""
        doc = VectorDocument(
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            content=chunk.content,
            embedding=embedding,
            metadata=chunk.metadata
        )
        self.documents.append(doc)

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 8,
        score_threshold: float = 0.0,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Performs semantic similarity search with optional metadata filtering.
        """
        results: List[Dict[str, Any]] = []

        for doc in self.documents:
            # Check metadata filter if provided
            if filter_metadata:
                match = True
                for k, v in filter_metadata.items():
                    if doc.metadata.get(k) != v:
                        match = False
                        break
                if not match:
                    continue

            score = cosine_similarity(query_embedding, doc.embedding)
            if score >= score_threshold:
                results.append({
                    "chunkId": doc.chunk_id,
                    "documentId": doc.document_id,
                    "content": doc.content,
                    "metadata": doc.metadata,
                    "score": round(score, 4)
                })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

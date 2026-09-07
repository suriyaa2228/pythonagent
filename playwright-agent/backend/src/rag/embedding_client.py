"""
Mistral AI Embedding Client
===========================
Provides embeddings for framework chunks and user queries using Mistral AI Embedding API,
with a fallback deterministic embedding generator for offline/local environments.
"""

import hashlib
import json
import math
import os
import urllib.request
from typing import List, Optional


class MistralEmbeddingClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_key = api_key or os.environ.get("MISTRAL_API_KEY", "")
        self.model = model or os.environ.get("MISTRAL_EMBEDDING_MODEL", "mistral-embed")
        self.api_url = "https://api.mistral.ai/v1/embeddings"
        self.dimension = 1024

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a batch of strings."""
        if not texts:
            return []

        # If API key is available, call Mistral API
        if self.api_key:
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                payload = {
                    "model": self.model,
                    "input": texts
                }
                req = urllib.request.Request(
                    self.api_url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers,
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=15) as response:
                    data = json.loads(response.read().decode("utf-8"))
                    return [item["embedding"] for item in data.get("data", [])]
            except Exception as e:
                print(f"[WARN] Mistral API request failed: {e}. Falling back to deterministic embedding.")

        # Fallback deterministic pseudo-embedding (useful for local development and testing)
        return [self._generate_local_embedding(text) for text in texts]

    def get_embedding(self, text: str) -> List[float]:
        """Generates embedding for a single string."""
        return self.get_embeddings([text])[0]

    def _generate_local_embedding(self, text: str) -> List[float]:
        """Generates a normalized deterministic dense vector from text hash and tokens."""
        vector = [0.0] * self.dimension
        words = text.lower().split()
        if not words:
            return vector

        for word in words:
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dimension
            vector[idx] += 1.0

        # L2 normalize
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]
        return vector

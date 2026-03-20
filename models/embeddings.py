import numpy as np
import google.generativeai as genai
from openai import OpenAI

from config.config import EMBEDDING_PROVIDERS


class EmbeddingModel:
    """Unified embedding model supporting Google and OpenAI providers."""

    def __init__(self, provider="google", api_key=None):
        self.provider = provider
        self.api_key = api_key
        self.config = EMBEDDING_PROVIDERS[provider]
        self.dimension = self.config["dimension"]
        self._initialize()

    def _initialize(self):
        try:
            if self.provider == "google":
                genai.configure(api_key=self.api_key)
            elif self.provider == "openai":
                self.client = OpenAI(api_key=self.api_key)
        except Exception as e:
            raise ConnectionError(f"Failed to initialize embedding model: {e}")

    def embed(self, texts):
        """Generate embeddings for one or more texts. Returns numpy array."""
        if isinstance(texts, str):
            texts = [texts]

        try:
            if self.provider == "google":
                return self._google_embed(texts)
            elif self.provider == "openai":
                return self._openai_embed(texts)
        except Exception as e:
            raise RuntimeError(f"Embedding failed ({self.provider}): {e}")

    def _google_embed(self, texts):
        embeddings = []
        batch_size = 20
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            result = genai.embed_content(
                model=self.config["model"],
                content=batch,
                task_type="retrieval_document",
            )
            embeddings.extend(result["embedding"])
        return np.array(embeddings, dtype=np.float32)

    def _openai_embed(self, texts):
        response = self.client.embeddings.create(
            model=self.config["model"],
            input=texts,
        )
        embeddings = [item.embedding for item in response.data]
        return np.array(embeddings, dtype=np.float32)

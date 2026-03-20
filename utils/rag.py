import faiss
import numpy as np

from config.config import TOP_K_RESULTS, SIMILARITY_THRESHOLD


class RAGEngine:
    """FAISS-backed retrieval engine for document Q&A."""

    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
        self.index = None
        self.chunks = []
        self.source_map = []

    def add_documents(self, chunks, source_name="document"):
        """Embed and index a list of text chunks."""
        try:
            if not chunks:
                return

            embeddings = self.embedding_model.embed(chunks)
            dimension = embeddings.shape[1]

            if self.index is None:
                self.index = faiss.IndexFlatIP(dimension)

            faiss.normalize_L2(embeddings)
            self.index.add(embeddings)
            self.chunks.extend(chunks)
            self.source_map.extend([source_name] * len(chunks))
        except Exception as e:
            raise RuntimeError(f"Failed to index documents: {e}")

    def search(self, query, top_k=TOP_K_RESULTS):
        """Return the most relevant chunks for a query."""
        if self.index is None or self.index.ntotal == 0:
            return []

        try:
            query_embedding = self.embedding_model.embed(query)
            faiss.normalize_L2(query_embedding)

            k = min(top_k, self.index.ntotal)
            scores, indices = self.index.search(query_embedding, k)

            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0 and score >= SIMILARITY_THRESHOLD:
                    results.append({
                        "text": self.chunks[idx],
                        "score": float(score),
                        "source": self.source_map[idx],
                    })
            return results
        except Exception as e:
            raise RuntimeError(f"RAG search failed: {e}")

    def clear(self):
        """Reset the index and all stored data."""
        self.index = None
        self.chunks = []
        self.source_map = []

    @property
    def document_count(self):
        return len(set(self.source_map))

    @property
    def chunk_count(self):
        return len(self.chunks)

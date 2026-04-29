from src.rag.embeddings import EmbeddingsService
from src.rag.vector_store import VectorStore
from src.utils.logger import logger

class Retriever:
    def __init__(self):
        self.embeddings = EmbeddingsService()
        self.vector_store = VectorStore()

    def retrieve_context(self, query, top_k=3):
        logger.info(f"Retrieving context for: {query[:50]}...")
        query_vector = self.embeddings.encode([query])[0]
        return self.vector_store.search(query_vector, top_k=top_k)

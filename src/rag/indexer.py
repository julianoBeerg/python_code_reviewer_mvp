import os
from src.rag.embeddings import EmbeddingsService
from src.rag.vector_store import VectorStore
from src.utils.logger import logger

class Indexer:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.embeddings = EmbeddingsService()
        self.vector_store = VectorStore()

    def run_indexing(self):
        logger.info(f"Starting indexing of markdown files in {self.repo_path}")
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Split content into chunks (simple for now: by paragraph)
                    chunks = [c.strip() for c in content.split("\n\n") if c.strip()]
                    
                    for chunk in chunks:
                        vector = self.embeddings.encode([chunk])[0]
                        self.vector_store.add(f"File: {file}\nContent: {chunk}", vector)
        
        self.vector_store.save()
        logger.info("Indexing completed")

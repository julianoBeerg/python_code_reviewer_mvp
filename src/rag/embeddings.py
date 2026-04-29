from sentence_transformers import SentenceTransformer
from src.utils.logger import logger

class EmbeddingsService:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        logger.info(f"Loading embeddings model: {model_name}")
        self.model = SentenceTransformer(model_name)

    def encode(self, texts):
        return self.model.encode(texts)

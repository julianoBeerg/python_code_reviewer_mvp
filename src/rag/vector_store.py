import numpy as np
import json
import os
from src.utils.logger import logger

class VectorStore:
    def __init__(self, index_path=".index/vectors.json"):
        self.index_path = index_path
        self.data = [] # List of {"text": str, "vector": list}
        self.load()

    def load(self):
        if os.path.exists(self.index_path):
            with open(self.index_path, "r") as f:
                self.data = json.load(f)
            logger.info(f"Loaded {len(self.data)} vectors from {self.index_path}")

    def save(self):
        with open(self.index_path, "w") as f:
            json.dump(self.data, f)
        logger.info(f"Saved {len(self.data)} vectors to {self.index_path}")

    def add(self, text, vector):
        self.data.append({"text": text, "vector": vector.tolist() if isinstance(vector, np.ndarray) else vector})

    def search(self, query_vector, top_k=3):
        if not self.data:
            return []
        
        vectors = np.array([item["vector"] for item in self.data])
        query_vector = np.array(query_vector)
        
        # Simple cosine similarity
        similarities = np.dot(vectors, query_vector) / (np.linalg.norm(vectors, axis=1) * np.linalg.norm(query_vector))
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        return [self.data[i]["text"] for i in top_indices]

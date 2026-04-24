import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer

class VectorRetriever:
    """
    Carrega os embeddings do disco e busca o contexto mais relevante para um dado Diff.
    Calcula a semelhança por similaridade de cossenos.
    """
    def __init__(self, index_dir: str = ".index"):
        self.index_file = os.path.join(index_dir, "vector_store.json")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vectors = []
        
        if os.path.exists(self.index_file):
            with open(self.index_file, 'r', encoding='utf-8') as f:
                self.vectors = json.load(f)

    def cosine_similarity(self, v1, v2):
        """Calcula a similaridade do cosseno entre dois vetores."""
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0
        return dot_product / (norm_v1 * norm_v2)

    def search(self, query: str, top_k: int = 3) -> str:
        """
        Gera o vetor da busca e acha os top_k chunks mais parecidos.
        Retorna uma string concatenada com o contexto.
        """
        if not self.vectors:
            return "Nenhum contexto local foi indexado. Considere rodar a indexação primeiro."
            
        query_embedding = self.model.encode(query)
        
        scored_results = []
        for item in self.vectors:
            score = self.cosine_similarity(query_embedding, item["embedding"])
            scored_results.append({
                "score": score,
                "content": item["content"],
                "file": item["file"]
            })
            
        # Ordena do maior pro menor score
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Pega os top_k
        top_results = scored_results[:top_k]
        
        # Formata o retorno
        context_str = ""
        for res in top_results:
            context_str += f"--- Extraído do arquivo: {res['file']} ---\n"
            context_str += f"{res['content']}\n\n"
            
        return context_str

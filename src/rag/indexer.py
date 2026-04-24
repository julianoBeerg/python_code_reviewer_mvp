import os
import json
import glob
from sentence_transformers import SentenceTransformer

class LocalIndexer:
    """
    Varre os arquivos do projeto (focado em .md), extrai o texto e gera
    embeddings usando sentence-transformers, salvando em um arquivo JSON local.
    """
    def __init__(self, repo_path: str, index_dir: str = ".index"):
        self.repo_path = repo_path
        self.index_dir = index_dir
        self.model = SentenceTransformer('all-MiniLM-L6-v2') # Modelo leve e rápido
        
        if not os.path.exists(self.index_dir):
            os.makedirs(self.index_dir)
            
        self.index_file = os.path.join(self.index_dir, "vector_store.json")

    def chunk_text(self, text: str, max_words: int = 200) -> list[str]:
        """Quebra textos longos em pedaços (chunks) menores."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), max_words):
            chunk = " ".join(words[i:i + max_words])
            chunks.append(chunk)
        return chunks

    def index_markdown_files(self):
        """Lê arquivos .md, gera os embeddings e salva."""
        print(f"Iniciando indexação do repositório em: {self.repo_path}")
        
        # Encontra todos os arquivos .md no repositório (recursivamente)
        search_pattern = os.path.join(self.repo_path, "**", "*.md")
        md_files = glob.glob(search_pattern, recursive=True)
        
        vectors = []
        
        for file_path in md_files:
            # Ignorar diretórios ocultos ou do node_modules/venv
            if ".git" in file_path or "venv" in file_path or "node_modules" in file_path:
                continue
                
            print(f"Lendo: {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                chunks = self.chunk_text(content)
                for i, chunk in enumerate(chunks):
                    # Gera o vetor
                    embedding = self.model.encode(chunk).tolist()
                    
                    vectors.append({
                        "file": file_path,
                        "chunk_index": i,
                        "content": chunk,
                        "embedding": embedding
                    })
            except Exception as e:
                print(f"Aviso: Não foi possível ler {file_path} - {str(e)}")

        # Salva o "banco de dados" vetorial no disco
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(vectors, f)
            
        print(f"Indexação concluída! {len(vectors)} chunks salvos em {self.index_file}")

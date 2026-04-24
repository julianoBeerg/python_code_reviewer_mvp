import json
from src.adapters.gitlab_adapter import GitLabAdapter
from src.adapters.github_adapter import GitHubAdapter
from src.adapters.llm_provider import LLMProvider
from src.rag.retriever import VectorRetriever
import os

class ReviewEngine:
    """
    Orquestrador principal: Junta Git (GitHub/GitLab), RAG e Gemini para fazer a revisão.
    """
    def __init__(self, platform: str = "gitlab"):
        self.platform = platform.lower()
        
        # Inicializa o adapter de Git correto com base na escolha
        if self.platform == "github":
            self.git_adapter = GitHubAdapter()
        else:
            self.git_adapter = GitLabAdapter()
            
        self.llm = LLMProvider()
        self.retriever = VectorRetriever()

    def run_review(self, target_project: str, merge_request_id: int):
        """
        Executa o fluxo completo para um Pull/Merge Request.
        target_project pode ser o ID (GitLab) ou "user/repo" (GitHub).
        """
        print(f"Buscando DIFF da PR/MR #{merge_request_id} no {self.platform.upper()}...")
        
        if self.platform == "github":
            diff_text = self.git_adapter.get_pr_diff(target_project, merge_request_id)
        else:
            diff_text = self.git_adapter.get_mr_diff(target_project, merge_request_id)
        
        if not diff_text:
            print("Não foi possível encontrar mudanças (diff) para esta solicitação.")
            return

        print("Recuperando contexto das diretrizes e READMEs do projeto via RAG...")
        context_data = self.retriever.search(query=diff_text, top_k=3)
        
        print("Enviando Diff + Contexto para a IA Revisora (Gemini)...")
        review_result = self.llm.generate_review(diff_text, context_data)
        
        print("Revisão gerada pela IA (Raw JSON):")
        print("="*40)
        print(review_result)
        print("="*40)
        
        # Tenta parsear o JSON retornado pela IA
        try:
            review_json = json.loads(review_result)
        except Exception as e:
            print(f"⚠️ Erro ao parsear JSON da IA. Postando como comentário simples. Erro: {str(e)}")
            review_json = None

        print(f"Postando resultado no {self.platform.upper()}...")
        if self.platform == "github":
            if review_json:
                self.git_adapter.post_inline_comments(target_project, merge_request_id, review_json)
            else:
                # Fallback se o JSON falhar
                repo = self.git_adapter.gh.get_repo(target_project)
                pr = repo.get_pull(merge_request_id)
                pr.create_issue_comment(review_result)
        else:
            # GitLab ainda usa o formato antigo (ajustar depois se necessário)
            self.git_adapter.post_comment_on_mr(target_project, merge_request_id, review_result)
            
        print("Fluxo concluído com sucesso!")

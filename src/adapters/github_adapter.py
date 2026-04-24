import os
from github import Github
from dotenv import load_dotenv

load_dotenv()

class GitHubAdapter:
    """
    Gerencia a comunicação com a API do GitHub.
    """
    def __init__(self):
        token = os.getenv("TOKEN_GITHUB")
        if not token or token.strip() == "":
            raise ValueError("ERRO: A variável TOKEN_GITHUB está vazia ou não foi configurada nos Secrets do GitHub.")
            
        # Autentica no GitHub
        self.gh = Github(token)
        
    def get_pr_diff(self, repo_name: str, pr_number: int) -> str:
        """
        Busca as mudanças (diff) de um Pull Request específico.
        """
        try:
            repo = self.gh.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            
            # O GitHub possui uma forma de pegar os arquivos modificados e seus patchs (diffs)
            diff_text = ""
            for file in pr.get_files():
                diff_text += f"Arquivo modificado: {file.filename}\n"
                diff_text += f"--- DIFF ---\n{file.patch}\n"
                diff_text += "="*40 + "\n"
                
            return diff_text
            
        except Exception as e:
            print(f"Erro ao buscar Diff do GitHub: {str(e)}")
            return ""

    def post_inline_comments(self, repo_name: str, pr_number: int, review_json: dict):
        """
        Publica comentários linha a linha no Pull Request.
        """
        try:
            repo = self.gh.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            
            # Pega o commit mais recente para associar o comentário
            last_commit = pr.get_commits().reversed[0]
            
            comments = []
            for comment_data in review_json.get("comments", []):
                comments.append({
                    "path": comment_data["file"],
                    "line": int(comment_data["line"]),
                    "body": comment_data["text"]
                })
            
            if comments:
                # Cria uma revisão completa com múltiplos comentários
                pr.create_review(
                    commit=last_commit,
                    body=review_json.get("summary", "AI Code Review"),
                    event="REQUEST_CHANGES" if review_json.get("status") == "CHANGES_REQUESTED" else "COMMENT",
                    comments=comments
                )
                print(f"✅ Revisão com {len(comments)} comentários inline postada no GitHub!")
            else:
                # Apenas aprova se não houver comentários
                pr.create_review(
                    commit=last_commit,
                    body=review_json.get("summary", "Código aprovado pela IA!"),
                    event="APPROVE"
                )
                print(f"✅ PR Aprovado no GitHub!")
                
        except Exception as e:
            print(f"Erro ao publicar comentários inline no GitHub: {str(e)}")

import os
import gitlab
from dotenv import load_dotenv

load_dotenv()

class GitLabAdapter:
    """
    Gerencia a comunicação com a API do GitLab.
    """
    def __init__(self):
        url = os.getenv("GITLAB_URL", "https://gitlab.com")
        token = os.getenv("GITLAB_TOKEN")
        
        if not token:
            raise ValueError("GITLAB_TOKEN não encontrado no arquivo .env")
            
        # Autentica no GitLab
        self.gl = gitlab.Gitlab(url=url, private_token=token)
        
    def get_mr_diff(self, project_id: str, mr_iid: int) -> str:
        """
        Busca as mudanças (diff) de um Merge Request específico.
        """
        try:
            project = self.gl.projects.get(project_id)
            mr = project.mergerequests.get(mr_iid)
            
            # Pega as mudanças (diffs) do MR
            changes = mr.changes()
            diff_text = ""
            
            for change in changes.get('changes', []):
                diff_text += f"Arquivo modificado: {change.get('new_path')}\n"
                diff_text += f"--- DIFF ---\n{change.get('diff')}\n"
                diff_text += "="*40 + "\n"
                
            return diff_text
            
        except Exception as e:
            print(f"Erro ao buscar Diff do GitLab: {str(e)}")
            return ""

    def post_comment_on_mr(self, project_id: str, mr_iid: int, comment: str):
        """
        Publica um comentário no Merge Request com o resultado do Code Review.
        """
        try:
            project = self.gl.projects.get(project_id)
            mr = project.mergerequests.get(mr_iid)
            
            # Adiciona a nota (comentário) no MR
            mr.notes.create({'body': comment})
            print(f"✅ Comentário publicado com sucesso no MR #{mr_iid}!")
            
        except Exception as e:
            print(f"Erro ao publicar comentário no GitLab: {str(e)}")

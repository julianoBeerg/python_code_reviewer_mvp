import click
import os
from dotenv import load_dotenv

from src.rag.indexer import LocalIndexer
from src.core.review_engine import ReviewEngine

# Garante que as variáveis do .env estejam carregadas
load_dotenv()

@click.group()
def cli():
    """🤖 Ferramenta CLI de Inteligência de Code Review."""
    pass

@cli.command()
@click.option('--repo', required=True, type=click.Path(exists=True), help="Caminho local para o repositório.")
def index(repo):
    """
    Lê os arquivos .md do projeto e cria a base de vetores local (RAG).
    """
    click.echo(f"Iniciando indexação local de RAG para o repositório: {repo}")
    indexer = LocalIndexer(repo_path=repo)
    indexer.index_markdown_files()
    click.echo("Indexação pronta!")

@cli.command()
@click.option('--pr-id', required=True, type=int, help="ID do Pull Request/Merge Request.")
@click.option('--platform', type=click.Choice(['github', 'gitlab']), default='github', help="Plataforma de hospedagem do código (github ou gitlab).")
def review(pr_id, platform):
    """
    Executa a revisão de código em um PR/MR do GitHub ou GitLab.
    """
    # Define o projeto/repositório com base na plataforma
    if platform == 'github':
        target_project = os.getenv("GITHUB_REPO")
        if not target_project:
            click.echo("ERRO: GITHUB_REPO não encontrado no arquivo .env (Ex: 'seu-usuario/seu-repo')")
            return
    else:
        target_project = os.getenv("GITLAB_PROJECT_ID")
        if not target_project:
            click.echo("ERRO: GITLAB_PROJECT_ID não encontrado no arquivo .env")
            return
            
    try:
        engine = ReviewEngine(platform=platform)
        engine.run_review(target_project=target_project, merge_request_id=pr_id)
    except Exception as e:
        click.echo(f"Ocorreu um erro durante a execução: {str(e)}")

if __name__ == '__main__':
    cli()

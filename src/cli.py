import click
from src.utils.logger import logger
from src.core.review_engine import ReviewEngine
from src.rag.indexer import Indexer

@click.group()
def cli():
    """Deep Review Service CLI"""
    pass

@cli.command()
@click.option("--pr-id", "--mr-id", required=True, type=int, help="Pull Request ID")
@click.option("--repo-name", "--project-id", help="GitHub repository (e.g., 'owner/repo'). Defaults to GITHUB_REPO in .env")
@click.option("--platform", help="Legacy option (ignored)")
def review(pr_id, repo_name, platform=None):
    """Run an AI review on a specific GitHub Pull Request"""
    try:
        engine = ReviewEngine()
        engine.execute_review_flow(pr_id, repo_name)
    except Exception as e:
        logger.error(f"Review failed: {e}")

@cli.command()
@click.option("--repo-path", "--repo", required=True, help="Path to local repository to index for RAG")
def index(repo_path):
    """Index a local repository (markdown files) for RAG"""
    try:
        indexer = Indexer(repo_path)
        indexer.run_indexing()
    except Exception as e:
        logger.error(f"Indexing failed: {e}")

if __name__ == "__main__":
    cli()

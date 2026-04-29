from github import Github
from src.config import settings
from src.utils.logger import logger

class GitHubAdapter:
    """
    Handles communication with GitHub API.
    """
    def __init__(self):
        if not settings.github_token:
            logger.error("GITHUB_TOKEN not found in settings")
            raise ValueError("GITHUB_TOKEN is required")
        
        self.gh = Github(settings.github_token)
        logger.info("Authenticated with GitHub")

    def fetch_pull_request_diff(self, repo_name: str, pr_id: int) -> list[dict]:
        """
        Fetches the diff of a pull request and returns a list of file changes.
        """
        try:
            repo = self.gh.get_repo(repo_name)
            pr = repo.get_pull(pr_id)
            
            diffs = []
            for file in pr.get_files():
                diffs.append({
                    "new_path": file.filename,
                    "diff": file.patch if file.patch else ""
                })
            
            logger.info(f"Fetched diff for PR #{pr_id} in {repo_name} ({len(diffs)} files)")
            return diffs
        except Exception as e:
            logger.error(f"Error fetching PR diff: {e}")
            raise

    def post_review_comment(self, repo_name: str, pr_id: int, body: str):
        """
        Posts a review comment to the pull request.
        """
        try:
            repo = self.gh.get_repo(repo_name)
            pr = repo.get_pull(pr_id)
            pr.create_issue_comment(body)
            logger.info(f"Posted review comment to PR #{pr_id}")
        except Exception as e:
            logger.error(f"Error posting comment: {e}")
            raise

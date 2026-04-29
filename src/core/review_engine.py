from src.adapters.github_adapter import GitHubAdapter
from src.adapters.llm_provider import LLMProvider
from src.rag.retriever import Retriever
from src.utils.logger import logger
from src.config import settings

class ReviewEngine:
    def __init__(self):
        self.github = GitHubAdapter()
        self.llm = LLMProvider()
        self.retriever = Retriever()

    def execute_review_flow(self, pr_id: int, repo_name: str = None):
        """
        Orchestrates the full review process: fetch diff, retrieve context, generate review, and post comment.
        """
        repo_name = repo_name or settings.github_repo
        if not repo_name:
            raise ValueError("Repository name is required (pass --repo-name or set GITHUB_REPO in .env)")

        logger.info(f"Starting review flow for PR #{pr_id} in {repo_name}")
        
        # 1. Fetch Pull Request Diffs
        changes = self.github.fetch_pull_request_diff(repo_name, pr_id)
        diff_text = ""
        for change in changes:
            diff_text += f"File: {change['new_path']}\nDiff:\n{change['diff']}\n\n"
        
        if not diff_text:
            logger.warning("No diff found for this PR.")
            return

        # 2. Retrieve relevant context (RAG)
        context = self.retriever.retrieve_context(diff_text[:1000])
        context_text = "\n\n".join(context)
        
        # 3. Construct Prompt
        prompt = self._build_prompt(diff_text, context_text)
        
        # 4. Generate Review using LLM
        review_md = self.llm.generate_review(prompt)
        
        # 5. Post Review Comment to GitHub
        self.github.post_review_comment(repo_name, pr_id, review_md)
        logger.info("Review flow completed successfully")

    def _build_prompt(self, diff_text: str, context_text: str) -> str:
        return f"""
You are a senior software engineer performing a code review.
Use the following context from project documentation to guide your review:
---
{context_text}
---

Analyze the following diff and provide a structured review with focus on:
1. Code quality and best practices.
2. Potential bugs or edge cases.
3. Alignment with project documentation provided in the context.

Diff:
---
{diff_text}
---

Provide your review in Markdown format.
"""

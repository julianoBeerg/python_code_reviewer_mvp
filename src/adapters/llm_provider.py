import google.generativeai as genai
from src.config import settings
from src.utils.logger import logger

class LLMProvider:
    def __init__(self):
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')
            logger.info("Configured Gemini LLM Provider")
        else:
            logger.error("GEMINI_API_KEY not found in settings")
            raise ValueError("GEMINI_API_KEY is required")

    def generate_review(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating review: {e}")
            raise

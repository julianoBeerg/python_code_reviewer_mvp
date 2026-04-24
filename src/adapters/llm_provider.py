import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class LLMProvider:
    """
    Abstração para chamadas de LLM usando a biblioteca moderna google-genai (2026).
    """
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY não encontrada")
            
        # Inicializa o cliente moderno
        self.client = genai.Client(api_key=self.api_key)
        
        # Modelo preferencial para 2026
        self.model_name = os.getenv("LLM_MODEL", "gemini-2.0-flash")
        
        self.system_instruction = (
            "Você é um Auditor de Segurança rigoroso. "
            "Sua única tarefa é encontrar falhas, especialmente Hardcoded Secrets e falhas de lógica. "
            "Retorne APENAS um JSON puro, sem blocos de código markdown."
        )

    def generate_review(self, diff_data: str, context_data: str) -> str:
        """
        Tenta gerar a revisão usando a API moderna.
        """
        prompt = f"""
CONTEXTO: {context_data}
DIFF: {diff_data}

FORMATO JSON:
{{
  "summary": "resumo",
  "comments": [ {{"file": "x", "line": 1, "text": "y"}} ],
  "status": "APPROVED" ou "CHANGES_REQUESTED"
}}
"""
        # Lista de modelos para tentar em 2026
        models_to_try = [self.model_name, "gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"]
        
        for model_id in models_to_try:
            try:
                print(f"🤖 Tentando API Moderna com: {model_id}...")
                response = self.client.models.generate_content(
                    model=model_id,
                    contents=prompt,
                    config={
                        "system_instruction": self.system_instruction,
                        "temperature": 0
                    }
                )
                return response.text.strip()
            except Exception as e:
                print(f"⚠️ Falha com {model_id}: {str(e)}")
                continue
                
        return "Erro: Nenhum modelo disponível na API moderna."

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class LLMProvider:
    """
    Abstração para chamadas de LLM.
    Configurado para usar Google Gemini (Plano Gratuito via AI Studio).
    """
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("LLM_MODEL", "gemini-1.5-flash")
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY não encontrada no arquivo .env")
            
        # Configura a API do Google
        genai.configure(api_key=self.api_key)
        
        # Inicializa o modelo
        # system_instruction é suportado a partir do gemini-1.5-pro e gemini-1.5-flash
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction="Você é um Arquiteto de Software Senior realizando um Code Review rigoroso e instrutivo."
        )

    def generate_review(self, diff_data: str, context_data: str) -> str:
        """
        Constrói o prompt e solicita a revisão ao Gemini.
        """
        prompt = f"""
Por favor, revise o código abaixo baseado no contexto fornecido.

CONTEXTO DO PROJETO (Regras e Padrões):
---
{context_data}
---

MUDANÇAS NO CÓDIGO (GIT DIFF):
---
{diff_data}
---

Instruções de Revisão:
1. Verifique se o código respeita as regras e padrões arquiteturais definidos no CONTEXTO.
2. Identifique potenciais bugs, problemas de segurança ou ineficiências de performance.
3. Se houver problemas, você DEVE retornar a resposta EXATAMENTE no formato JSON abaixo:
{{
  "summary": "Resumo geral da revisão",
  "comments": [
    {{
      "file": "nome_do_arquivo.py",
      "line": 10,
      "text": "Explicação detalhada do problema e sugestão"
    }}
  ],
  "status": "APPROVED" ou "CHANGES_REQUESTED"
}}

4. Se o código estiver perfeito, use status "APPROVED" e deixe a lista de comments vazia.
5. NÃO inclua blocos de código markdown (como ```json) na sua resposta, retorne APENAS o JSON puro.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Erro ao gerar revisão pelo Gemini: {str(e)}"

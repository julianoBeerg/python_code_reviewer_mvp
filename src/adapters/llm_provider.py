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
        
        # Inicializa o modelo com instruções de Auditor de Segurança
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=(
                "Você é um Auditor de Segurança rigoroso. "
                "Sua única tarefa é encontrar falhas, especialmente Hardcoded Secrets (chaves, senhas) e falhas de lógica. "
                "NÃO seja complacente. Se houver uma string fixa que parece uma chave, peça mudanças."
            ),
            generation_config={
                "temperature": 0,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
            }
        )

    def generate_review(self, diff_data: str, context_data: str) -> str:
        """
        Constrói o prompt e solicita a revisão ao Gemini com foco em segurança.
        """
        prompt = f"""
Você deve realizar um Code Review focado em SEGURANÇA e BOAS PRÁTICAS.

CONTEXTO DO PROJETO:
---
{context_data}
---

MUDANÇAS NO CÓDIGO (GIT DIFF):
---
{diff_data}
---

CHECKLIST DE REVISÃO (CRÍTICO):
1. HARDCODED SECRETS: Verifique se há chaves de API, senhas, tokens ou 'Master Keys' escritas diretamente no código. Isso é PROIBIDO.
2. INJECTION: Busque por SQL Injection ou comandos de shell que concatenam variáveis diretamente.
3. PADRÕES: Verifique se o código segue as regras do CONTEXTO acima.
4. BUGS: Identifique erros de lógica ou fluxos que podem quebrar em produção.

FORMATO DE RESPOSTA (OBRIGATÓRIO JSON):
Você deve retornar APENAS um JSON no formato abaixo. Se encontrar qualquer problema de segurança, status deve ser "CHANGES_REQUESTED".

{{
  "summary": "Resumo crítico da revisão",
  "comments": [
    {{
      "file": "nome_do_arquivo.java",
      "line": 10,
      "text": "🚨 ALERTA DE SEGURANÇA: [Explicação do erro e como corrigir usando variáveis de ambiente ou Vault]"
    }}
  ],
  "status": "APPROVED" ou "CHANGES_REQUESTED"
}}

Se o código estiver 100% seguro e seguir os padrões, retorne status "APPROVED" e lista de comments vazia.
NÃO use blocos de código ```json. Retorne o texto puro.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Erro ao gerar revisão pelo Gemini: {str(e)}"

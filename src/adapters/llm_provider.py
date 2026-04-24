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
        # Tentando o modelo Deep Research que apareceu na sua lista
        self.model_name = os.getenv("LLM_MODEL", "deep-research-preview-04-2026")
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY não encontrada no arquivo .env")
            
        # Configura a API do Google
        genai.configure(api_key=self.api_key)
        
        # Diagnóstico: Listar modelos disponíveis
        try:
            print("--- MODELOS DISPONÍVEIS PARA ESTA CHAVE ---")
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    print(f"ID: {m.name}")
            print("-------------------------------------------")
        except Exception as e:
            print(f"Erro ao listar modelos: {str(e)}")

        # Guarda a instrução de sistema para usar nos fallbacks
        self.system_instruction_text = (
            "Você é um Auditor de Segurança rigoroso. "
            "Sua única tarefa é encontrar falhas, especialmente Hardcoded Secrets (chaves, senhas) e falhas de lógica. "
            "NÃO seja complacente. Se houver uma string fixa que parece uma chave, peça mudanças."
        )

        # Inicializa o modelo base
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=self.system_instruction_text,
            generation_config={
                "temperature": 0,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
            }
        )

    def generate_review(self, diff_data: str, context_data: str) -> str:
        """
        Tenta gerar a revisão usando uma lista de modelos de fallback.
        """
        # Lista de modelos para tentar (do mais moderno para o mais compatível)
        models_to_try = [
            self.model_name,
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-2.0-flash-exp",
            "gemini-pro"
        ]
        
        last_error = ""
        
        for model_id in models_to_try:
            try:
                print(f"🤖 Tentando revisão com o modelo: {model_id}...")
                current_model = genai.GenerativeModel(
                    model_name=model_id,
                    system_instruction=self.system_instruction_text,
                    generation_config=self.model.generation_config
                )
                
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
{{
  "summary": "Resumo crítico da revisão",
  "comments": [
    {{
      "file": "nome_do_arquivo.java",
      "line": 10,
      "text": "🚨 ALERTA DE SEGURANÇA: [Explicação]"
    }}
  ],
  "status": "APPROVED" ou "CHANGES_REQUESTED"
}}
APENAS JSON PURO.
"""
                response = current_model.generate_content(prompt)
                return response.text.strip()
                
            except Exception as e:
                last_error = str(e)
                print(f"⚠️ Falha com {model_id}: {last_error}")
                continue
                
        return f"Erro crítico: Nenhum dos modelos disponíveis ({models_to_try}) funcionou ou tem cota. Último erro: {last_error}"

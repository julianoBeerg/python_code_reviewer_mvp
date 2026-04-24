# 🤖 Inteligência de Code Review (MVP)

Este é o MVP do assistente de Code Review automatizado. Ele utiliza a **API Gratuita do Gemini 1.5 Flash** para fazer análises de código em Merge Requests do GitLab, aplicando as regras de negócio encontradas nos arquivos Markdown (.md) do seu repositório local usando um sistema RAG (Retriever-Augmented Generation) 100% offline e sem custos.

## 🛠️ Onde Colocar as Chaves e Conexões

Todas as credenciais ficam no arquivo **`.env`** (que não deve ser comitado).
Eu já criei um arquivo base chamado `.env.example`.

1. Duplique o `.env.example` e renomeie para `.env`.
2. Preencha as seguintes informações no `.env`:

```env
# 1. GERANDO O TOKEN DO GITLAB:
# Vá no seu GitLab -> Edit Profile -> Access Tokens -> Add new token.
# Dê permissão de "api" e "read_repository".
GITLAB_URL=https://gitlab.com  # ou a URL do seu GitLab on-premise
GITLAB_TOKEN=seu_token_gerado_aqui

# Como achar o PROJECT_ID? 
# Na página principal do seu repositório no GitLab, o "Project ID" fica logo abaixo do nome do projeto.
GITLAB_PROJECT_ID=1234567 

# 2. GERANDO A CHAVE DO GEMINI (100% Gratuito):
# Acesse: https://aistudio.google.com/
# Faça login com uma conta Google e clique em "Get API key" -> "Create API key".
GEMINI_API_KEY=sua_chave_do_google_aqui
LLM_MODEL=gemini-1.5-flash
```

---

## 🚀 Como Rodar o Projeto Passo a Passo

### Passo 1: Instalar as Dependências
Abra o terminal na pasta do projeto e instale as bibliotecas necessárias:
```bash
pip install -r requirements.txt
```

### Passo 2: Indexar as Regras do seu Projeto (RAG Local)
Para que a Inteligência Artificial "entenda" os padrões da sua empresa/projeto, ela precisa ler os arquivos `.md` (como o README).
Execute o comando abaixo apontando para o repositório que você deseja que a IA estude:

```bash
# Exemplo: indexando este próprio repositório
python -m src.cli index --repo ./
```
*Isso vai criar uma pasta `.index/` oculta com os vetores matemáticos dos seus textos.*

### Passo 3: Rodar o Code Review em um Merge Request Real
Agora que a IA já tem o contexto e suas chaves estão no `.env`, escolha um Merge Request aberto no seu GitLab (pegue o número do MR, ex: `!42` -> ID é `42`).

Execute:
```bash
python -m src.cli review --mr-id 42
```

### 🧠 Como a Mágica Acontece (Fluxo)?

1. **CLI (`src/cli.py`)**: Recebe o ID do MR e inicia a `ReviewEngine`.
2. **GitLab Adapter (`src/adapters/gitlab_adapter.py`)**: Conecta no seu GitLab e baixa o "Diff" (apenas o que mudou no código).
3. **RAG Retriever (`src/rag/retriever.py`)**: Lê o diff e busca na pasta `.index/` quais regras (arquivos .md) são relevantes para essas mudanças.
4. **Gemini Adapter (`src/adapters/llm_provider.py`)**: Pega o *Código que mudou* + *Regras da Empresa* e pede pro Gemini: *"Você é um arquiteto sênior. Avalie esse código com base nestas regras."*
5. **GitLab Adapter**: Pega a resposta do Gemini e publica um comentário direto no seu Merge Request no GitLab!

---

## 📁 Estrutura de Arquivos Criada
- `src/cli.py`: A porta de entrada do programa.
- `src/core/review_engine.py`: O "cérebro" que coordena as chamadas.
- `src/adapters/llm_provider.py`: Comunicação com o Gemini AI.
- `src/adapters/gitlab_adapter.py`: Comunicação com a API do GitLab.
- `src/rag/indexer.py`: Transforma seus `.md` em vetores usando IA local (`sentence-transformers`).
- `src/rag/retriever.py`: Faz buscas semânticas nos vetores para achar as regras certas na hora do Code Review.

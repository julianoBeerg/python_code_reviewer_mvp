
## 🎯 MVP Refinado - Arquitetura Monolítica Local

### 📦 Stack Simplificado

```
┌─────────────────────────────────┐
│   CLI Entry Point               │
│   (dispara análise local)       │
├─────────────────────────────────┤
│   Review Engine (orquestrador)  │
├─────────────────────────────────┤
│   LLM Provider (abstração)       │
│   ├─ OpenAI API (cloud)         │
│   └─ Ollama (local fallback)    │
├─────────────────────────────────┤
│   RAG Minimal                    │
│   ├─ File Indexer (local)       │
│   └─ Embeddings (SentenceT5)   │
├─────────────────────────────────┤
│   GitLab Adapter                │
│   ├─ Diff Parser                │
│   └─ MR Comments Publisher      │
├─────────────────────────────────┤
│   Local Storage:                │
│   ├─ SQLite + Vector ext        │
│   └─ .index/ folder             │
└─────────────────────────────────┘
```

---

### 🛠️ Tech Stack MVP

| Componente | Tech | Peso |
|-----------|------|------|
| **Linguagem** | **Python 3.11+** | Leve, ótimo para IA |
| **Framework** | **FastAPI** (opcional) ou **Click** (CLI) | CLI é suficiente para MVP |
| **LLM** | **OpenAI API** (cloud) | Não precisa de GPU local |
| **Embeddings** | **sentence-transformers** (local) | Roda offline |
| **Vector DB** | **SQLite + sqlite-vec** ou **Milvus Lite** | Sem servidor externo |
| **GitLab** | **python-gitlab** | Integração nativa |
| **Config** | **python-dotenv** | Secrets seguros |

---

### 📁 Estrutura de Pastas (Monolito)

```
deep-review-service/
├── src/
│   ├── __init__.py
│   ├── cli.py                 # Entry point
│   ├── config.py              # Configs
│   │
│   ├── core/
│   │   ├── review_engine.py   # Orquestrador
│   │   └── rules.py           # Regras de negócio
│   │
│   ├── adapters/
│   │   ├── gitlab_adapter.py  # GitLab integration
│   │   ├── llm_provider.py    # LLM abstraction
│   │   └── embeddings.py      # Embeddings service
│   │
│   ├── rag/
│   │   ├── indexer.py         # Indexação
│   │   ├── retriever.py       # Recuperação
│   │   └── vector_store.py    # SQLite + embeddings
│   │
│   ├── domain/
│   │   ├── diff_analyzer.py   # Parse diff
│   │   ├── review.py          # Domain models
│   │   └── context.py         # Context builder
│   │
│   └── utils/
│       ├── logger.py
│       └── helpers.py
│
├── .index/                    # Índices locais
├── .env.example
├── requirements.txt
├── pyproject.toml
├── pytest.ini
├── README.md
└── pitch.md (seu current)
```

---

## 🚀 Fluxo do MVP

```
1. gitlab-review --mr-id 123 --repo ~/my-repo
       ↓
2. Diff extraído via GitLab API
       ↓
3. Diff parsing → identifica arquivos alterados
       ↓
4. RAG minimal: recupera docs relevantes (.md files no repo)
       ↓
5. Prompt estruturado enviado para OpenAI/Ollama
       ↓
6. Resposta: comentário estruturado (Markdown)
       ↓
7. Publicado no GitLab MR
```

---

## 💾 RAG Minimalista (MVP)

**Escopo inicial:**
- Indexar apenas arquivos `.md` + README.md do repositório
- Embeddings via `sentence-transformers` (roda local, offline)
- Vector store em SQLite com extensão
- Recuperação: top-3 documentos relevantes por semelhança

```python
# Pseudocódigo
indexer = LocalIndexer(repo_path="~/my-repo")
indexer.index_markdown_files()  # Scan .md files

retriever = VectorRetriever(index_path=".index/")
context = retriever.search(
    query="qual é o padrão de error handling?",
    top_k=3
)
# context → ["doc1.md", "doc2.md"] com trechos
```

---

## 🎮 Exemplo de Uso (MVP)

```bash
# Setup
pip install -r requirements.txt
cp .env.example .env
# Editar .env: GITLAB_TOKEN, OPENAI_API_KEY

# Indexar repo (rodar 1x)
python -m src.cli index --repo /path/to/repo

# Analisar PR específico
python -m src.cli review --mr-id 42

# Ou via CI/CD (GitLab Runner)
gitlab-review --mr-id $CI_MERGE_REQUEST_IID
```

---

## 🎯 Próximas Fases (Especialização)

### Fase 1 (MVP agora)
- ✅ Monolito Python
- ✅ RAG básico (MD files)
- ✅ LLM API
- ✅ GitLab sync

### Fase 2 (Specialização)
- Separar em serviços:
  - `review-core` (engine)
  - `rag-service` (índices)
  - `llm-gateway` (pool de modelos)

### Fase 3 (Escala)
- Add Kubernetes
- Webhook server (em vez de CLI)
- Job queue (Celery)

---

## ❓ Decisões Finais para o MVP

**1. LLM:**
- Recomendo começar com **OpenAI GPT-4** (confiável)
- Fallback: **Ollama local** (Mistral 7B ou Llama 2) se quiser zero-cloud

**2. Vector DB:**
- Recomendo **sqlite-vec** (zero setup, embarcado)
- Alternativa: **Milvus Lite** (se precisar mais features depois)

**3. Contexto mínimo:**
- Phase 1: apenas `.md` files (README, design docs)
- Phase 2: adicionar imports + class definitions
- Phase 3: histórico de commits/PRs
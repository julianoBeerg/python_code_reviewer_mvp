# 🏗️ Arquitetura e Esteira CI/CD

## 🔄 Fluxo de Integração Contínua (Esteira)

O MVP foi desenhado para ser executado como um Job dentro do pipeline do GitLab.

### Exemplo de `.gitlab-ci.yml`:

```yaml
stages:
  - analyze

ai_code_review:
  stage: analyze
  image: python:3.11
  only:
    - merge_requests
  variables:
    GITLAB_TOKEN: $PROJECT_ACCESS_TOKEN
    OPENAI_API_KEY: $OPENAI_API_KEY
  script:
    - pip install -r requirements.txt
    - # Opcional: Baixar índice pré-construído ou indexar rapidamente
    - python -m src.cli index --repo . 
    - # Executa a revisão no MR atual
    - python -m src.cli review --mr-id $CI_MERGE_REQUEST_IID --project-id $CI_PROJECT_ID
  allow_failure: true # Não bloqueia o pipeline se a IA falhar
```

## 🧩 Componentes do Sistema

### 1. Context Review Engine
O orquestrador (`src/core/review_engine.py`) recebe o ID do Merge Request, solicita o diff ao GitLab, busca contexto relevante no RAG e envia tudo para o LLM.

### 2. RAG (Retrieval-Augmented Generation)
- **Indexer**: Varre arquivos `.md`, `README.md` e cabeçalhos de código para criar uma base de conhecimento local.
- **Retriever**: Com base no código alterado no diff, busca documentos que explicam as regras de negócio ou padrões arquiteturais relacionados.

### 3. GitLab Adapter
Responsável por usar a API do GitLab para:
1. Obter o Diff do Merge Request.
2. Publicar comentários linha a linha ou um sumário geral no MR.

## 📈 Evolução do MVP
- **Fase 1**: CLI manual e análise de arquivos Markdown para contexto.
- **Fase 2**: Análise de dependências de código e histórico de commits.
- **Fase 3**: Interface Web para o desenvolvedor validar os comentários da IA antes de publicar (Human-in-the-loop).

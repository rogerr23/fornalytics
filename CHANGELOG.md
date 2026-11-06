# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/). Uma seção por fase do plano de construção.

## [Não lançado]

### Fase 5 — lentes (visão geral e chat)
- Prompts das três lentes e das tarefas `overview.md` e `chat.md`.
- `GET /overview?lens=` (SSE): gerada na primeira abertura de cada lente e depois servida do cache; respostas com erro não são guardadas.
- `POST /chat` (SSE) com base + arquivos relevantes (ranking sem embeddings, limitado por `CHAT_MAX_FILES` e `CHAT_CONTEXT_TOKENS`) e as últimas `CHAT_HISTORY_TURNS` trocas.
- `GET /conversations/{id}` para remontar o chat depois de recarregar a página.
- Marcadores `[[caminho:Lx-Ly]]` conferidos ao fim de cada resposta e enviados no evento `citations`; erro com o stream aberto vira o evento `error`.
- Contrato dos eventos em `docs/api-events.md`; prompts v2 em `docs/prompts.md`.

### Fase 4 — base do produto
- Modelos `ProductBase`, `Evidence`, `Promise` e `FeatureStatus`, que servem também de schema da saída estruturada.
- Extração em duas etapas (promessas da ideia → base do código); só código ou só documento usam uma chamada.
- Reconciliação sem IA: uma feature por promessa, promessa esquecida vira `documented_only`, referência desconhecida vira `undocumented`.
- Validação de citações (arquivo, linhas e trecho curto ignorando espaços); as inválidas são descartadas da base.
- Prompts `base.md`, `extraction_idea.md`, `extraction.md` e o `PromptBuilder`.
- `POST /process` (202, em segundo plano; 409 se já estiver processando; 422 sem fontes), `GET /status` (SSE) e `GET /base`.
- Gravação da base, limpeza do cache e `base_outdated = false` numa transação; projetos presos em `processing` viram `failed` ao subir o servidor.
- `docs/api-events.md`, `docs/prompts.md` e o formato do JSONB em `docs/data-model.md`.

### Fase 3 — ingestão
- Migração: remove `comparisons` e adiciona `projects.base_outdated` (ADR 0002).
- Rotas de projetos (`POST/GET /projects`, `GET /projects/{id}`) e de fontes (`POST/GET /sources`, `DELETE /sources/{id}`, `GET /files?path=`), com os primeiros repositórios e serviços.
- Ingestão no envio: extratores de zip, PDF (com marcadores de página), DOCX e texto; filtros (pastas, lockfiles, binários, minificados, segredos, arquivos grandes, caminhos inseguros).
- Limites de upload, de tamanho descompactado real e de número de arquivos; mensagens em português.
- Corte por prioridade por etapa (documentos e código) com lista do que fica de fora; `MAX_CONTEXT_TOKENS` passa a 200 mil; `CHAT_HISTORY_TURNS` no `.env.example`.
- Caminhos repetidos ganham sufixo; adicionar ou remover fonte marca a base como desatualizada.
- `docs/ingestion.md`.

### Revisão do fluxo (antes da Fase 3)
- Ingestão passa a acontecer no envio de cada fonte, com resumo imediato; o processamento faz só a extração pela IA.
- Material acima do limite entra por prioridade, e o que fica de fora é listado na tela.
- Ideia × Código derivado da base (extração em duas etapas); `comparisons` e `POST /idea-vs-code` saem do plano ([ADR 0002](docs/adr/0002-ideia-x-codigo-derivado-da-base.md)).
- Lado a lado em uma chamada; fluxo como JSON com o Mermaid montado no backend.
- Remoção de fonte e aviso de base desatualizada (`projects.base_outdated`).
- Trecho de citação curto, visão geral sob demanda e histórico do chat limitado (`CHAT_HISTORY_TURNS`).
- Atualizados `CLAUDE.md`, `docs/data-model.md`, `docs/architecture.md`, `docs/llm.md` e o documento de produto.

### Fase 2 — provedores de IA
- Interface `LLMProvider` (`generate`, `stream`, `generate_json`) com `GeminiProvider` (google-genai), `OllamaProvider` (HTTP) e `FakeProvider` (testes).
- `RetryingProvider`: novas tentativas em 429 e 5xx, até 3, sem esperar mais de 30s e sem repetir streaming já iniciado.
- Erros amigáveis em português (`QuotaExceeded`, `ProviderUnavailable`, `ProviderNotConfigured`, `InvalidModelOutput`).
- `npm run llm:check` e `npm run llm:models`; `/api/health` e a página inicial mostram a IA configurada.
- Modelo padrão `gemini-3.5-flash`; `docs/llm.md`.

### Fase 1 — banco de dados
- Conexão assíncrona com PostgreSQL (SQLAlchemy 2 + psycopg 3), compatível com a conexão pooled do Neon.
- 8 tabelas com ids UUID, datas com fuso, exclusão em cascata e valores fixos validados no banco.
- Alembic assíncrono com a migração inicial; scripts `npm run migrate` e `npm run migration:new`.
- `/api/health` informa o estado do banco; a página inicial mostra "Banco: ok".
- Testes de integração no branch `test` do Neon, com rollback e pulados quando não configurados.
- `docs/data-model.md` e seção de configuração do Neon no README.

### Fase 0 — base do projeto
- Comandos do projeto como scripts npm na raiz (`setup`, `dev`, `test`, `lint`, `format`, `migrate`), funcionando em Windows, macOS e Linux.
- Backend FastAPI gerenciado com `uv`: `create_app()`, configurações via `pydantic-settings`, erro de domínio com handler único, logging e `GET /api/health`.
- Frontend React + Vite + TypeScript estrito com Tailwind CSS, TanStack Query, React Router, ESLint e Prettier; página inicial mostra o status da API.
- `.env.example` com todas as variáveis, `.gitignore`, `.gitattributes`.
- `README.md`, `docs/architecture.md` e ADR 0001.

### Planejamento

- `CLAUDE.md` com decisões técnicas, estrutura de código, padrões de projeto e plano de documentação.
- Documento de produto v2 (`fornalytics-projeto.md`).
- Pasta `docs/` com índice, modelo de ADR e diário de construção.

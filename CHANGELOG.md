# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/). Uma seção por fase do plano de construção.

## [Não lançado]

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

# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/). Uma seção por fase do plano de construção.

## [Não lançado]

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

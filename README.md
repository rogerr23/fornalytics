# Fornalytics

Lê o material de um produto digital (código, documento da ideia, transcrição ou texto livre) e explica esse produto em três lentes: **cliente**, **não técnico** e **técnico**.

- Documento de produto: [`fornalytics-projeto.md`](fornalytics-projeto.md)
- Guia técnico (decisões, arquitetura, plano): [`CLAUDE.md`](CLAUDE.md)
- Documentação viva: [`docs/`](docs/README.md)

---

## Pré-requisitos

Funciona em **Windows, macOS e Linux**.

| Ferramenta | Para quê | Como instalar |
|---|---|---|
| [Git](https://git-scm.com/downloads) | Clonar o projeto | Site oficial |
| [Node.js LTS](https://nodejs.org/) | Frontend e comandos do projeto | Site oficial |
| [uv](https://docs.astral.sh/uv/) | Backend Python (instala o Python 3.12 sozinho) | Veja abaixo |

Instalar o `uv`:

- **macOS / Linux:**
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Windows (PowerShell):**
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

Depois de instalar, feche e abra o terminal e confira com `uv --version`.

---

## Rodando do zero

```bash
git clone <url-do-repositorio> fornalytics
cd fornalytics
```

Crie o `.env` a partir do exemplo:

- macOS / Linux: `cp .env.example .env`
- Windows (PowerShell): `Copy-Item .env.example .env`

Instale tudo e suba o projeto:

```bash
npm run setup
npm run dev
```

| Endereço | O que é |
|---|---|
| http://localhost:5173 | Aplicação |
| http://localhost:8000/api/health | Saúde da API |
| http://localhost:8000/docs | Documentação interativa da API |

Para parar, use `Ctrl+C` no terminal.

---

## Comandos

Todos rodam a partir da raiz do projeto.

| Comando | O que faz |
|---|---|
| `npm run setup` | Instala as dependências da raiz, do backend e do frontend |
| `npm run dev` | Sobe backend (8000) e frontend (5173) juntos |
| `npm test` | Roda os testes |
| `npm run lint` | Confere lint e formatação (backend e frontend) |
| `npm run format` | Formata o código |
| `npm run migrate` | Aplica as migrações do banco (a partir da Fase 1) |

---

## Estrutura

```
fornalytics/
├── backend/     # API em Python (FastAPI), gerenciada com uv
├── frontend/    # Interface em React + Vite + TypeScript
├── docs/        # Documentação viva
└── demo/        # App de exemplo para a demonstração (Fase 10)
```

Detalhes das camadas e das regras de código em [`docs/architecture.md`](docs/architecture.md).

---

## Variáveis de ambiente

Todas estão listadas e comentadas em [`.env.example`](.env.example). Na Fase 0 nenhuma é obrigatória.

> O `.env` nunca vai para o Git.

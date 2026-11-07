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

Configure o banco (veja [Banco de dados](#banco-de-dados-neon) abaixo), depois instale tudo, crie as tabelas e suba o projeto:

```bash
npm run setup
npm run migrate
npm run dev
```

| Endereço | O que é |
|---|---|
| http://localhost:5173 | Aplicação (mostra se backend, banco e IA estão ok) |
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
| `npm test` | Roda os testes (backend com pytest, frontend com vitest) |
| `npm run lint` | Confere lint e formatação (backend e frontend) |
| `npm run format` | Formata o código |
| `npm run migrate` | Aplica as migrações do banco |
| `npm run migration:new -- -m "descricao"` | Gera uma migração nova a partir dos models |
| `npm run llm:check` | Confere a IA configurada (1 chamada real) |
| `npm run llm:models` | Lista os modelos Flash do Gemini disponíveis para a sua chave |
| `npm run demo:zip` | Gera `demo/loja.zip`, o código da loja de exemplo para enviar na demo |
| `npm run eval` | Roda o conjunto de avaliação com a IA real (gasta cota; veja abaixo) |

---

## Banco de dados (Neon)

O banco é um PostgreSQL gratuito no [Neon](https://neon.tech). Cada pessoa pode usar o mesmo projeto do Neon (dados compartilhados) ou criar o seu.

1. Crie uma conta e um projeto no Neon (região **AWS São Paulo**). Quando perguntar por serviços extras, escolha **Just Postgres**.
2. No painel do projeto, clique em **Connect** e copie duas strings:
   - com **Connection pooling** ligado (endereço com `-pooler`) → `DATABASE_URL`;
   - com **Connection pooling** desligado → `DATABASE_URL_DIRECT`.
3. Em **Branches**, crie um branch `test` a partir do `production`, com **Auto-delete: Never**. No **Connect**, escolha esse branch e copie a string pooled → `TEST_DATABASE_URL`.
4. Cole as três no `.env` como vieram do Neon e rode `npm run migrate`.

Sem `TEST_DATABASE_URL`, os testes de banco são pulados. Detalhes das tabelas em [`docs/data-model.md`](docs/data-model.md).

---

## IA (Gemini)

A IA dentro do app é o Gemini no plano gratuito do Google AI Studio.

1. Crie uma chave em https://aistudio.google.com/apikey (conta Google, sem cartão).
2. No `.env`, preencha `GEMINI_API_KEY`. `LLM_PROVIDER=gemini` e `GEMINI_MODEL=gemini-3.5-flash` já vêm no exemplo.
3. Confira (faz uma chamada real):
   ```bash
   npm run llm:check
   ```

Para ver os modelos disponíveis para a sua chave: `npm run llm:models`. Ollama (modelo local, opcional), limites e erros em [`docs/llm.md`](docs/llm.md).

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

### Usando a interface

Com `npm run dev` rodando, abra http://localhost:5173:

1. **Novo projeto** → dê um nome ao produto.
2. **Material:** envie o código (`.zip`) e, se tiver, o documento da ideia (PDF, DOCX, MD ou TXT) ou cole um texto. Cada envio mostra os arquivos lidos, os ignorados e o que ficaria fora do limite.
3. **Processar:** a tela mostra cada etapa da IA. Pode levar alguns minutos, e recarregar a página não perde o progresso.
4. **Projeto:** escolha a lente (Cliente, Não técnico ou Técnico) no canto superior.
   - **Visão geral:** gerada na primeira abertura de cada lente; depois vem do cache.
   - **Chat:** perguntas na lente ativa.
   - **Lado a lado:** a mesma pergunta respondida nas três lentes ao mesmo tempo.
   - **Isso faz?:** Sim, Não ou Parcialmente, com a justificativa e as evidências.
   - **Ideia × Código:** o que foi prometido e implementado, o que foi prometido e não existe no código e o que existe sem estar documentado (sem chamar a IA).
   - **Fluxos:** os fluxos da base já aparecem desenhados; pergunte "o que acontece quando…?" para ver o passo a passo com diagrama.
   - Citações válidas abrem o trecho do arquivo; as que não conferem aparecem como "não verificada".
5. Se o material mudar depois do processamento, aparece o aviso **O material mudou** com o botão **Reprocessar**.

### Demo

O material da apresentação fica em `demo/`: a **Loja Aurora** (código) e o `escopo.md` (documento da ideia), com lacunas propositais. Veja [`demo/README.md`](demo/README.md) e o roteiro em [`docs/demo-script.md`](docs/demo-script.md).

### Avaliação (eval)

O conjunto de avaliação (`backend/evals/questions.yaml`) tem 50 perguntas sobre a Loja Aurora, cerca de 15 por lente mais o lado a lado, cada uma com o que se espera da resposta. Ele precisa do projeto **Loja Aurora (demo)** já processado.

```bash
npm run eval
```

- Cada pergunta é uma chamada à IA. O script espera alguns segundos entre as chamadas e salva o progresso: se a cota acabar, rode de novo depois e ele continua de onde parou.
- `npm run eval -- --core`: só o subconjunto rápido, para conferir depois de mudar um prompt.
- `npm run eval -- --only nt-09,tec-02 --redo`: refaz perguntas específicas.
- O relatório vai para `docs/evals/AAAA-MM-DD.md` e as respostas completas para `docs/evals/AAAA-MM-DD-respostas.md`. As perguntas do roteiro da demo viram respostas de reserva em `demo/reserva/`.

### Testando a API direto (sem frontend)

Com `npm run dev` rodando, abra http://localhost:8000/docs:

1. `POST /api/projects` → **Try it out** → `{"name": "Meu projeto"}`.
2. `POST /api/projects/{project_id}/sources` → escolha `type` (`code` para `.zip`) e o arquivo, ou `title` + `content` para colar texto.
3. A resposta mostra os arquivos usados, os ignorados e o que ficaria de fora do limite. Formatos, filtros e limites em [`docs/ingestion.md`](docs/ingestion.md).

---

## Variáveis de ambiente

Todas estão listadas e comentadas em [`.env.example`](.env.example). Hoje são necessárias as do banco e a `GEMINI_API_KEY`; sem elas a API sobe, mas a página inicial mostra o que falta.

> O `.env` nunca vai para o Git.

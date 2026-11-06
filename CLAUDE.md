# CLAUDE.md — Fornalytics

Este arquivo é a fonte de verdade técnica do projeto para o Claude Code. Leia-o inteiro antes de começar qualquer tarefa.
O documento de produto (problema, lentes, jornada, impacto) está em `fornalytics-projeto.md`.

---

## 1. O que é o Fornalytics

Uma aplicação web que lê o material de um produto digital (repositório de código, documento da ideia, transcrição de reunião ou texto livre), monta uma **base do produto** única e estruturada e explica esse produto em três **lentes**:

| Lente (`Lens`) | Público | Tom |
|---|---|---|
| `cliente` | Cliente final, stakeholders | Valor, benefícios, sem jargão, frases curtas |
| `nao_tecnico` | Comercial, atendimento, gestão | Como funciona na prática, analogias, fluxos simples |
| `tecnico` | Devs, Tech Lead | Arquitetura, arquivos, funções, integrações, **sempre com citação de arquivo e linhas** |

**Regra de ouro:** as lentes mudam a forma, nunca a essência. Todas derivam da mesma base do produto.

Contexto: protótipo do Programa de Estágio Extreme Group (Desafio de IA com Claude). O projeto é **construído com o Claude Code e o Cowork**; a IA que roda dentro do app é gratuita (ver seção 3).

---

## 2. Decisões já tomadas (não reabrir sem o Roger pedir)

| Tema | Decisão |
|---|---|
| Nome | Fornalytics |
| Abordagem | Opção C: prompts validados primeiro, depois a interface |
| Lentes | Três lentes fixas (sem slider de profundidade) |
| Diferencial principal | **Ideia × Código** |
| Diferenciais extras | "Isso o produto faz?", modo **lado a lado** (mesma pergunta nas 3 lentes) e fluxo com diagrama Mermaid |
| Fora do escopo | Tudo da seção 4.3 do documento de produto (vai para "próximos passos") e a trilha de onboarding com quiz |
| Backend | Python 3.12 + FastAPI |
| Frontend | React + Vite + TypeScript |
| Banco | PostgreSQL no **Neon** (plano gratuito) |
| IA em execução | **Gemini (plano gratuito do Google AI Studio)** como principal e **Ollama** local como reserva |
| Custo | **Zero.** Nunca adicionar serviço, biblioteca ou recurso pago |
| Portabilidade | Tem que rodar em qualquer computador com `git clone` + `.env` + um comando |

---

## 3. IA: camada de provedor

- Toda chamada de modelo passa por uma interface única `LLMProvider` em `backend/app/llm/`. Nenhum outro módulo importa SDK de modelo diretamente.
- Implementações:
  - `GeminiProvider`: SDK oficial `google-genai`. Modelo definido por `GEMINI_MODEL` no `.env` (usar um modelo **Flash** disponível no plano gratuito; conferir a lista atual no AI Studio, não fixar versão no código).
  - `OllamaProvider`: API HTTP local do Ollama (`OLLAMA_BASE_URL`, `OLLAMA_MODEL`).
- Seleção por `LLM_PROVIDER=gemini|ollama`, **só manual** (sem fallback automático entre provedores). Deve ser fácil acrescentar um `ClaudeProvider` no futuro sem mexer no resto.
- O Ollama é reserva para chat e visão geral; a extração da base (de onde sai o Ideia × Código) e o lado a lado (saída estruturada) funcionam melhor no Gemini (modelos locais pequenos erram JSON estruturado). Documentar isso em `docs/llm.md`.
- Métodos mínimos: `generate(system, messages) -> str`, `stream(system, messages) -> AsyncIterator[str]` e `generate_json(system, messages, schema: type[BaseModel]) -> BaseModel` (saída estruturada).
- **Plano gratuito tem limite e oscila.** Tratar erro 429 (cota) **e 5xx (alta demanda, comum no Gemini gratuito)** com nova tentativa e espera exponencial (máx. 3 tentativas, nunca esperar mais de 30s) e devolver uma mensagem amigável ao frontend. As novas tentativas do próprio SDK ficam desligadas. Detalhes em `docs/llm.md`.
- **Economizar cota:** a extração da base roda uma vez por projeto (2 chamadas: ideia e código, seção 4.2) e fica salva no banco. Visões gerais por lente são geradas **sob demanda** (na primeira abertura de cada lente) e ficam em cache no banco. O Ideia × Código não chama a IA (sai da base) e o lado a lado é **uma** chamada para as 3 lentes.
- O conteúdo enviado ao plano gratuito do Gemini pode ser usado pelo Google: **usar apenas o repositório de demo próprio ou projetos open source.**

---

## 4. Arquitetura e pipeline

```
POST /sources (sem IA, na hora)        POST /process (IA, em segundo plano)        Lentes
Upload ──▶ Ingestão ──▶ resumo   ──▶   (a) promessas da ideia ──▶ (b) base do   ──▶ visão geral, chat,
(zip, pdf,  (texto puro, (arquivos,         (só se houver doc)        código com       lado a lado, "Isso faz?",
 docx, md,   linhas       ignorados,                                  status de cada   Ideia × Código (agrupa a
 txt, texto) numeradas)   tokens, o que                               promessa, JSONB) base, sem IA), fluxo
                          ficou de fora)
```

A ingestão acontece **no envio** de cada fonte; o processamento faz só a extração pela IA. Assim a pessoa vê o tamanho do material e o que ficou de fora antes de gastar cota.

### 4.1 Ingestão (`backend/app/ingestion/`)
- `.zip`: `zipfile` da biblioteca padrão. `.pdf`: `pdfplumber`. `.docx`: `python-docx`. `.md`, `.txt` e texto colado: direto.
- Ignorar: `node_modules`, `.git`, `dist`, `build`, `.next`, `venv`, `.venv`, `__pycache__`, lockfiles, imagens, fontes, binários, arquivos minificados e arquivos acima de 200 KB.
- Priorizar: README, rotas/controllers, models/schemas, services, config.
- Cada arquivo de código é salvo com caminho relativo e conteúdo. Ao montar o contexto para o modelo, renderizar com linhas numeradas:
  ```
  === src/services/payment.ts ===
  1| import ...
  2| ...
  ```
- A ingestão roda **dentro do `POST /sources`** (síncrona, sem IA). Guardar só o **texto extraído** no banco; o arquivo original é descartado ao fim da requisição. A resposta traz o resumo: arquivos usados, arquivos ignorados (com o motivo agrupado), tokens estimados e o que ficaria de fora do limite.
- Estimar tokens pela heurística **caracteres ÷ 4** (sem chamar API).
- **Corte por prioridade:** o limite `MAX_CONTEXT_TOKENS` (padrão 200 mil) vale **por etapa da extração**: documentos (etapa a) de um lado, código (etapa b) do outro. Quando um grupo passa do limite, os arquivos entram pela ordem de prioridade acima enquanto couberem; os que ficam de fora são listados na tela (nunca corte silencioso). A mesma função (`ingestion/selection.py`) serve ao chat (seção 4.4).
- Também são ignorados `.env` e chaves (`.pem`, `.key`) de dentro do zip, para não mandar segredos à IA; `.env.example` entra.
- **Caminhos repetidos no projeto** ganham sufixo (`README.md` → `README (2).md`), para cada citação apontar para um único arquivo.
- **Segurança do upload** (limites no `.env`): `MAX_UPLOAD_MB` (padrão 20), `MAX_UNZIPPED_MB` (padrão 100) e `MAX_FILES` (padrão 2000). Ler o zip entrada por entrada, somando o tamanho descompactado e parando ao passar do limite; ignorar caminhos absolutos ou com `..`.

### 4.2 Base do produto (`backend/app/extraction/`)
Modelo Pydantic `ProductBase`, gerado com saída estruturada e salvo em `JSONB`:
- `summary`, `stack`, `entities`, `integrations`
- `features[]`: `name`, `description`, `status` (`implemented` | `partial` | `documented_only` | `undocumented`), `evidence[]`
- `flows[]`: `name`, `steps[]`, `evidence[]`
- `business_rules[]`: `rule`, `evidence[]`
- `evidence`: `{source_type, path, line_start, line_end, quote}`. O `quote` é **curto** (um trecho de até ~120 caracteres de dentro do intervalo, não o bloco inteiro), para economizar tokens de saída e evitar que a base venha cortada.

**Extração em duas etapas** (o Ideia × Código sai daqui, sem chamada própria):
1. **Promessas** (`extraction_idea.md`): se houver documento da ideia, transcrição ou texto, extrair a lista de funcionalidades prometidas, com evidências no documento.
2. **Base** (`extraction.md`): extrair a `ProductBase` a partir do código, **recebendo a lista de promessas**. Cada promessa vira uma feature com `status` `implemented`, `partial` ou `documented_only` (não encontrada no código); o que existe no código e não foi prometido vira `undocumented`.

Casos: só código → pula a etapa 1 (sem `documented_only`/`undocumented`; o Ideia × Código pede o documento da ideia). Só documento → pula a leitura de código; a base descreve a ideia e as features ficam `documented_only`.

**Ideia × Código** = `features` agrupadas por status (✅ `implemented`/`partial`, ⚠️ `documented_only`, 🔍 `undocumented`). O "Isso faz?" lê o mesmo status, então os dois nunca se contradizem.

**Fluxo:** o modelo `Flow` tem `steps[]` (texto + evidências), `nodes[]` (`id`, `label`) e `edges[]` (`source`, `target`, `label`). O modelo de IA devolve só isso; o **backend monta o texto Mermaid** (`flowchart`) numa função pura. O diagrama nunca sai com sintaxe inválida.

**Modelos simples para a saída estruturada:** a saída estruturada do Gemini aceita só parte do JSON Schema. Todo modelo de `domain/` enviado como `schema` usa apenas tipos básicos, enums, listas e objetos aninhados. Proibido `dict` livre, unions e campos opcionais complexos.

### 4.3 Anti-alucinação (obrigatório)
- O prompt base manda responder **apenas** com o material e dizer "não encontrei no material" quando faltar base.
- **Validação de citações no backend:** toda evidência é conferida (o arquivo existe, as linhas existem e o trecho curto aparece dentro do intervalo de linhas, ignorando diferenças de espaço). Citação inválida é descartada ou marcada como `unverified`; nunca é exibida como verdade.
- No frontend, a citação válida vira um link que abre o trecho do arquivo.
- **Citações em respostas com streaming (chat):** o modelo escreve marcadores `[[caminho:L10-L20]]` no texto. O texto é transmitido como está; ao terminar, o backend valida todos os marcadores e envia um evento final `citations` com o resultado. O frontend troca cada marcador por link (válida) ou por um selo "não verificada".

### 4.4 Contexto enviado ao modelo (`lenses/context.py`)
- Extração da base: todo o material renderizado, cortado por prioridade em `MAX_CONTEXT_TOKENS` (seção 4.1).
- Chat, lado a lado, "Isso faz?" e fluxo: **base do produto + arquivos relevantes**, nunca o repositório inteiro.
- Chat: entram só as últimas `CHAT_HISTORY_TURNS` trocas da conversa (padrão 6), para o custo por pergunta ficar previsível.
- Seleção dos arquivos: ranking simples (palavras da pergunta no caminho e no conteúdo + arquivos citados nas evidências da base ligadas à pergunta), sem embeddings.
- Limites no `.env`: `CHAT_MAX_FILES` (padrão 8) e `CHAT_CONTEXT_TOKENS` (padrão 30000). Os arquivos entram em ordem de relevância até bater o primeiro dos dois limites.
- Como a base já resume o produto inteiro e aponta os arquivos de cada funcionalidade, o risco de perder um arquivo importante fica baixo.

### 4.5 Prompts (`backend/app/prompts/`)
- Arquivos `.md` versionados: `base.md`, `lens_cliente.md`, `lens_nao_tecnico.md`, `lens_tecnico.md`, `extraction_idea.md`, `extraction.md`, `overview.md`, `chat.md`, `compare_lenses.md`, `does_it.md`, `flow.md`. (Não há prompt de Ideia × Código: ele sai da base.)
- Prompt final = `base.md` + prompt da lente + tarefa. Usar o esboço da seção 6.4 do documento de produto como ponto de partida.
- Conjunto de avaliação em `backend/evals/questions.yaml` (cerca de 15 perguntas por lente, com o que se espera da resposta) para checar qualidade e consistência entre lentes.
- **Avaliação = checagens automáticas + revisão manual.** Um script confere o que é objetivo (citações válidas, "não encontrei no material" quando esperado, status certo no "Isso faz?"); o tom de cada lente o Roger revisa. Sem IA como juiz, para não gastar cota.

---

## 5. Banco de dados (Neon / PostgreSQL)

- SQLAlchemy 2.0 **assíncrono** (`AsyncSession`) + **Alembic** para migrações. Driver `psycopg` (v3) no modo assíncrono.
- `DATABASE_URL` = string de conexão **pooled** do Neon (`sslmode=require`), usada pela aplicação. `DATABASE_URL_DIRECT` = conexão direta, usada pelo Alembic.
- Conexão pooled passa por PgBouncer, que não suporta prepared statements: criar o engine com `connect_args={"prepare_threshold": None}`. Isso vale para qualquer PgBouncer, não é específico do Neon.
- O banco é só uma URL no `.env`: o código não pode ter nada específico do Neon.
- Tabelas (a migração inicial criou também `comparisons`; ela sai e `base_outdated` entra numa migração no início da Fase 3, ver ADR 0002):
  - `projects` (id, name, status: `draft|processing|ready|failed`, status_detail, base_outdated boolean, created_at)
  - `sources` (id, project_id, type: `code|idea_doc|transcript|text`, filename, created_at)
  - `source_files` (id, source_id, path, content, token_estimate)
  - `product_bases` (id, project_id, data JSONB, provider, model, created_at)
  - `lens_cache` (project_id, lens, kind: `overview`, content, created_at)
  - `conversations` (id, project_id, created_at) e `messages` (id, conversation_id, lens, role, content, citations JSONB, created_at)
- **Invalidação de cache:** ao reprocessar um projeto, apagar o `lens_cache` dele e zerar `base_outdated` na mesma transação que grava a nova base. Sem versionamento de bases (histórico está em "futuro").
- **Base desatualizada:** adicionar ou remover uma fonte de um projeto que já tem base marca `base_outdated = true`. A base anterior continua visível até o reprocessamento; a interface mostra o aviso "O material mudou".
- Ids em **UUID**. Campos com valores fixos (`status`, `lens`, `type`, `role`, `kind`) são **texto + CHECK**, não `ENUM` nativo; os valores ficam em `app/domain/enums.py`.
- `product_bases` tem **uma linha por projeto** (`project_id` único).
- Toda mudança de esquema vira uma migração Alembic. Nunca alterar tabela manualmente. Detalhes em `docs/data-model.md`.

---

## 6. API (FastAPI)

Prefixo `/api`. Respostas longas via **SSE** (Server-Sent Events).

| Método | Rota | Função |
|---|---|---|
| POST | `/projects` | Criar projeto |
| GET | `/projects`, `/projects/{id}` | Listar / detalhar |
| POST | `/projects/{id}/sources` | Formulário multipart com `type` e `file` **ou** `title` + `content` (texto colado); faz a ingestão na hora e devolve o resumo (arquivos usados/ignorados, tokens, o que fica de fora) |
| GET | `/projects/{id}/sources` | Lista as fontes do projeto |
| DELETE | `/projects/{id}/sources/{source_id}` | Remove uma fonte (marca a base como desatualizada) |
| POST | `/projects/{id}/process` | Dispara a extração pela IA (promessas + base) em segundo plano; responde na hora (202) |
| GET | `/projects/{id}/status` | Acompanha o processamento por SSE (lê `projects.status`; recarregar a página não perde nada) |
| GET | `/projects/{id}/base` | Base do produto |
| GET | `/projects/{id}/overview?lens=` | Visão geral na lente (gerada na primeira abertura, depois cache) |
| POST | `/projects/{id}/chat` | Pergunta na lente escolhida; resposta por SSE |
| POST | `/projects/{id}/compare-lenses` | Mesma pergunta nas 3 lentes, em **uma** chamada com saída estruturada (sem streaming) |
| POST | `/projects/{id}/does-it` | "Isso o produto faz?" → `sim | não | parcialmente` + justificativa + evidências |
| GET | `/projects/{id}/idea-vs-code` | Features da base agrupadas por status (sem chamar a IA) |
| POST | `/projects/{id}/flow` | Fluxo passo a passo + nós/arestas; o backend devolve também o texto Mermaid montado |
| GET | `/projects/{id}/conversations/{conversation_id}` | Mensagens de uma conversa do chat (para remontar a tela após recarregar) |
| GET | `/projects/{id}/files?path=` | Conteúdo de um arquivo (para abrir citações) |

**Processamento em segundo plano:** a tarefa roda no próprio processo do backend (sem fila externa) e grava cada etapa em `projects.status` / `status_detail`. Ao subir o servidor, projetos presos em `processing` viram `failed` com mensagem para reprocessar.

---

## 7. Frontend

- React + Vite + TypeScript, Tailwind CSS, TanStack Query, `react-markdown`, `mermaid`.
- Interface em **português do Brasil**.
- Telas: lista de projetos → criação/upload → processamento (progresso por etapas) → projeto com abas **Visão geral**, **Chat**, **Lado a lado**, **Isso faz?**, **Ideia × Código** e **Fluxos**.
- No upload, cada fonte mostra o resumo da ingestão logo após o envio (arquivos usados, ignorados, tokens) e, se passar do limite, um aviso com a lista do que fica de fora. Fontes podem ser removidas.
- No projeto, quando `base_outdated` for verdadeiro, um aviso "O material mudou" com botão **Reprocessar** aparece acima das abas.
- Seletor de lente sempre visível e alternável a qualquer momento.
- Ideia × Código em três colunas: ✅ prometido e implementado, ⚠️ prometido e não implementado, 🔍 implementado e não documentado.
- Erros de cota (429) aparecem como aviso amigável, nunca como tela quebrada.

---

## 8. Estrutura do repositório e padrões de código

### 8.1 Visão geral

```
fornalytics/
├── CLAUDE.md
├── fornalytics-projeto.md
├── README.md                 # como rodar em qualquer computador
├── CHANGELOG.md              # o que entrou em cada fase
├── .env.example
├── package.json              # só scripts: npm run setup, dev, test, lint, migrate (seção 9)
├── .gitattributes            # quebras de linha LF em qualquer sistema
├── docs/                     # documentação viva (seção 14)
├── backend/
├── frontend/
└── demo/                     # app de exemplo + escopo com lacunas propositais
```

### 8.2 Backend: camadas

```
backend/
├── pyproject.toml            # gerenciado com uv; config do ruff e do pytest aqui
├── alembic/
├── app/
│   ├── main.py               # create_app(): monta routers, CORS e handlers de erro
│   ├── core/
│   │   ├── config.py         # Settings (pydantic-settings), única leitura do .env
│   │   ├── errors.py         # exceções de domínio (NotFound, QuotaExceeded, ...)
│   │   └── logging.py
│   ├── domain/               # modelos Pydantic puros: Lens, ProductBase, Evidence,
│   │                         # IdeaVsCode (visão agrupada da base), DoesItAnswer, Flow.
│   │                         # Sem IO, sem imports internos.
│   ├── db/
│   │   ├── session.py        # engine e sessão
│   │   ├── models/           # tabelas SQLAlchemy (ORM), um arquivo por agregado
│   │   └── repositories/     # único lugar que escreve SQL/ORM; recebe e devolve domínio
│   ├── llm/
│   │   ├── base.py           # LLMProvider (interface)
│   │   ├── gemini.py         # GeminiProvider (adapter do google-genai)
│   │   ├── ollama.py         # OllamaProvider (adapter da API HTTP)
│   │   ├── errors.py         # erros amigáveis + sinais internos de "tente de novo"
│   │   ├── fake.py           # FakeProvider para testes
│   │   ├── retry.py          # RetryingProvider: nova tentativa no 429 e 5xx
│   │   ├── check.py          # npm run llm:check / llm:models
│   │   └── factory.py        # get_provider(settings) → LLMProvider
│   ├── projects/service.py   # ProjectService (criar, listar, detalhar)
│   ├── ingestion/
│   │   ├── extractors/       # um extractor por formato (zip, pdf, docx, text) + registro
│   │   ├── filters.py        # o que ignorar e o que priorizar
│   │   ├── selection.py      # corte por prioridade dentro de um limite de tokens
│   │   ├── limits.py         # limite por etapa (documentos, código) de um projeto
│   │   ├── rendering.py      # renderização com linhas numeradas
│   │   ├── tokens.py         # estimativa de tokens
│   │   └── service.py        # IngestionService
│   ├── extraction/service.py # ProductBaseService (gera e salva a base)
│   ├── citations/validator.py
│   ├── prompts/
│   │   ├── *.md              # base, lentes e tarefas (seção 4.5)
│   │   └── builder.py        # PromptBuilder: base + lente + tarefa
│   ├── lenses/               # um serviço por caso de uso:
│   │                         # overview, chat, compare, does_it, idea_vs_code, flow
│   │   └── context.py        # monta o contexto enviado ao modelo
│   └── api/
│       ├── deps.py           # injeção de dependências (Depends): sessão, provider, serviços
│       ├── sse.py            # helper de Server-Sent Events
│       ├── schemas/          # DTOs de request/response (separados do domínio)
│       └── routers/          # um router por recurso; finos, sem regra de negócio
├── evals/
└── tests/
    ├── unit/                 # espelha app/; sem banco e sem rede
    ├── integration/          # API + banco de teste, sempre com FakeProvider
    └── fixtures/             # zips, pdfs e textos pequenos de exemplo
```

**Regras de dependência (de cima para baixo, nunca o contrário):**

```
api/routers ──▶ serviços (ingestion, extraction, lenses) ──▶ domain
                     │                                    ──▶ db/repositories
                     └──────────────────────────────────▶ llm (só pela interface)
```

- `domain/` não importa nada do projeto.
- Routers só validam entrada, chamam um serviço e convertem a saída em DTO.
- Serviços recebem as dependências pelo construtor (provider, repositórios, settings). Nada de instância global; isso é o que permite trocar pelo `FakeProvider` nos testes.
- Só `db/repositories/` toca o ORM. Só `llm/` importa SDK de modelo. Só `core/config.py` lê variáveis de ambiente.
- Erros de domínio são exceções de `core/errors.py`, convertidas em HTTP num handler único em `main.py` (ex.: `QuotaExceeded` → 429 com mensagem amigável).

**Padrões de projeto usados (e só estes, sem inventar camada a mais):**

| Padrão | Onde | Para quê |
|---|---|---|
| Strategy + Adapter | `llm/` | Gemini, Ollama e futuramente Claude atrás da mesma interface |
| Decorator | `llm/retry.py` | `RetryingProvider` envolve qualquer provedor com a política de novas tentativas |
| Factory | `llm/factory.py` | Escolher o provedor pelo `LLM_PROVIDER` |
| Registry | `ingestion/extractors/` | Escolher o extractor pela extensão do arquivo; formato novo = arquivo novo |
| Repository | `db/repositories/` | Isolar o banco dos serviços |
| Service layer | `ingestion/`, `extraction/`, `lenses/` | Um caso de uso por serviço |
| Builder | `prompts/builder.py` | Montar prompt = base + lente + tarefa, sempre igual |
| Dependency Injection | `api/deps.py` | Montar os serviços por request e trocar em testes |
| DTO | `api/schemas/` | Contrato da API independente do modelo interno |

### 8.3 Frontend: por funcionalidade

```
frontend/src/
├── main.tsx
├── app/                      # App, rotas, providers (QueryClient, lente ativa)
├── pages/                    # telas; só compõem features, sem lógica própria
│   ├── ProjectsPage.tsx
│   ├── NewProjectPage.tsx
│   ├── ProcessingPage.tsx
│   └── ProjectPage.tsx       # abas
├── features/
│   ├── lens/                 # seletor e contexto da lente ativa
│   ├── upload/
│   ├── processing/
│   ├── overview/
│   ├── chat/
│   ├── compare/              # lado a lado
│   ├── does-it/
│   ├── idea-vs-code/
│   ├── flows/
│   └── citations/            # link de citação + visualizador de trecho
│       └── (cada feature: components/, hooks/, api.ts, types.ts)
└── shared/
    ├── api/                  # cliente HTTP, cliente SSE, tratamento de 429
    ├── ui/                   # componentes genéricos (Button, Card, Tabs, Alert...)
    └── lib/                  # utilitários puros
```

- Uma feature pode importar de `shared/`, nunca de outra feature. Se duas precisam da mesma coisa, ela sobe para `shared/`.
- Toda chamada à API passa por hooks do TanStack Query dentro da feature (`hooks/`), nunca `fetch` direto em componente.
- Componentes em PascalCase, um por arquivo; hooks começam com `use`.

---

## 9. Portabilidade e ambiente

- **Tem que funcionar em Windows, macOS e Linux.** Nada de comando que só existe em um sistema (Make, `rm -rf`, `export`, `&` no shell, caminhos com `/` fixos no Python — usar `pathlib`).
- Pré-requisitos: `uv`, Node LTS, Git. O Python 3.12 é instalado pelo próprio `uv` (`.python-version` no backend). Ollama só se for usar o provedor local.
- `.env.example` lista todas as variáveis: `LLM_PROVIDER`, `GEMINI_API_KEY`, `GEMINI_MODEL`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `DATABASE_URL`, `DATABASE_URL_DIRECT`, `MAX_CONTEXT_TOKENS`, `CHAT_MAX_FILES`, `CHAT_CONTEXT_TOKENS`, `CHAT_HISTORY_TURNS`, `MAX_UPLOAD_MB`, `MAX_UNZIPPED_MB`, `MAX_FILES`, `CORS_ORIGINS` e `TEST_DATABASE_URL` (só para testes de integração).
- `.env` **nunca** vai para o Git (garantir no `.gitignore`).
- **Comandos do projeto = scripts npm no `package.json` da raiz** (padrão do ecossistema, funciona igual em qualquer sistema, já que o Node é pré-requisito):

  | Comando | O que faz |
  |---|---|
  | `npm run setup` | Instala backend (`uv sync`) e frontend (`npm install`) |
  | `npm run dev` | Sobe backend (porta 8000) e frontend (porta 5173) juntos; Ctrl+C derruba os dois |
  | `npm test` | Testes do backend e do frontend |
  | `npm run lint` / `npm run format` | Confere / formata o código |
  | `npm run migrate` | Aplica as migrações Alembic |

- Os scripts chamam `uv --directory backend ...` e `npm --prefix frontend ...` (sem `cd`). Para rodar os dois servidores juntos, usar `concurrently` (dev, só na raiz).
- `.gitattributes` com `* text=auto eol=lf`, para o Windows não trocar as quebras de linha.
- O `README.md` deve permitir que outra pessoa rode o projeto do zero em outro computador.
- Docker não é obrigatório: o banco já está na nuvem.

---

## 10. Repositório de demo (`demo/`)

- Um app pequeno e próprio (ex.: loja simples com catálogo, carrinho, checkout e login).
- Um documento de escopo (`demo/escopo.md` ou PDF) com:
  - 2 funcionalidades prometidas e **não** implementadas (ex.: emissão de nota fiscal, cupom de desconto);
  - 1 funcionalidade implementada e **não** documentada;
  - o restante batendo com o código.
- Objetivo: resultado controlado e previsível para o Ideia × Código e para o "Isso faz?" na apresentação.

---

## 11. Plano de construção

Marque `[x]` ao concluir cada item e atualize esta lista no mesmo commit.

- [x] **Fase 0, base do projeto:** estrutura de pastas, `uv` + FastAPI com `/api/health`, Vite + React, `.env.example`, `.gitignore`, `.gitattributes`, `package.json` da raiz com os scripts, `README.md`, ruff/ESLint/Prettier configurados, `docs/architecture.md` e `CHANGELOG.md`
- [x] **Fase 1, banco:** conexão com o Neon, models, primeira migração Alembic
- [x] **Fase 2, provedor de IA:** `LLMProvider`, `GeminiProvider`, `OllamaProvider`, tratamento de 429
- [x] **Fase 3, ingestão:** migração (remove `comparisons`, adiciona `projects.base_outdated`), criação de projeto, upload com ingestão na hora e resumo, remoção de fonte, extração de texto, filtros, linhas numeradas, estimativa de tokens e corte por prioridade
- [x] **Fase 4, base do produto:** extração em duas etapas (promessas da ideia → base do código com status), validação de citações com trecho curto, processamento em segundo plano e progresso por SSE
- [x] **Fase 5, MVP de lentes:** visão geral por lente (com cache) e chat com streaming
- [x] **Fase 6, frontend do MVP:** upload, processamento, seletor de lente, visão geral e chat
- [x] **Fase 7, lado a lado (uma chamada para as 3 lentes) e "Isso faz?"**
- [ ] **Fase 8, Ideia × Código:** rota `GET` que agrupa a base por status e a tela em três colunas (sem chamada à IA)
- [ ] **Fase 9, fluxo com Mermaid:** modelo devolve passos, nós e arestas; o backend monta o Mermaid
- [ ] **Fase 10, demo:** app e escopo em `demo/`, rodar o fluxo completo de ponta a ponta
- [ ] **Fase 11, qualidade:** rodar o conjunto de avaliação, ajustar prompts, acabamento visual, respostas da demo salvas como reserva

---

## 12. Como trabalhar neste repositório

- **Código, nomes de variáveis, commits e comentários técnicos em inglês.** Interface, prompts das lentes, README e documentação em português do Brasil.
- Trabalhe **uma fase por vez**. Ao terminar, rode testes e lint, resuma o que foi feito e proponha o próximo passo.
- **Antes de começar cada fase, explique ao Roger por completo e espere o ok dele:**
  - objetivo da fase e como ela se encaixa no todo;
  - o que vai ser feito, passo a passo;
  - arquivos e pastas que serão criados ou alterados;
  - dependências novas (se houver);
  - testes que serão escritos;
  - **o que será criado ou atualizado nas docs** (`README.md`, `CHANGELOG.md`, `docs/*`, seção 11 deste arquivo);
  - como verificar que a fase terminou (critério de pronto).
- Python: `ruff` (lint e formatação), type hints em tudo, `pytest`. Frontend: ESLint + Prettier, TypeScript estrito.
- **Testes só no que é necessário.** Não sair testando tudo. Obrigatórios: ingestão (filtros, extração e limites do zip), validação de citações, parsing da saída estruturada, seleção de contexto (incluindo o corte por prioridade) e montagem do Mermaid. Fora disso, só teste de algo que já quebrou ou que é crítico na demo.
- Chamadas ao modelo nos testes usam o `FakeProvider`, nunca a API real.
- **Testes com banco:** poucos testes de integração, num branch separado do Neon (`TEST_DATABASE_URL`). Um engine por execução, cada teste dentro de uma transação desfeita no fim (rollback), sem criar/apagar tabelas a cada teste. Se o Neon ficar lento ou estourar limite, rever a estratégia (ex.: Postgres local).
- Commits pequenos, no padrão Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`…).
- **Quem commita é o Roger, no terminal dele.** O Claude nunca roda `git add`/`git commit`. Ao fechar uma unidade coerente de trabalho (não só no fim da fase), o Claude entrega os comandos prontos para copiar:
  - `git add` com os **arquivos listados explicitamente** (nunca `git add .` ou `-A`);
  - `git commit -m "..."` com mensagem em inglês no padrão Conventional Commits.
  - Antes de propor, confere `git status` e roda testes/lint do que foi mexido.
- **Dependências aprovadas** (além das citadas nas seções 3, 4, 5 e 7):
  - Backend: `fastapi`, `uvicorn[standard]`, `pydantic-settings`, `sqlalchemy[asyncio]`, `psycopg[binary]`, `alembic`, `python-multipart` (upload), `httpx` (Ollama), `pyyaml` (evals). Dev: `pytest`, `pytest-asyncio`, `ruff`.
  - Frontend: `react-router-dom`, `remark-gfm` (tabelas no Markdown das respostas). Dev: `vitest`, `@testing-library/react`, `eslint`, `prettier`.
  - Raiz (dev): `concurrently` (sobe backend e frontend juntos em qualquer sistema).
  - SSE feito com `StreamingResponse` do FastAPI no backend e `fetch` + leitura do stream no frontend, sem biblioteca extra.
- **Antes de adicionar uma dependência fora das listadas aqui, pergunte.** Nunca adicione algo pago.
- Se uma decisão nova for tomada, registre-a na seção 13 com data e motivo.
- Não implementar nada da seção 4.3 do documento de produto sem pedido explícito.

---

## 13. Registro de decisões

| Data | Decisão | Motivo |
|---|---|---|
| 2026-11-05 | Nome Fornalytics | Definido pelo Roger |
| 2026-11-05 | FastAPI + React (Vite) | Python é o melhor ecossistema para ler PDF, docx e zip; sem limite de tempo de execução |
| 2026-11-05 | Gemini gratuito + Ollama como reserva | Custo zero; contexto grande o bastante para o repositório inteiro. O desafio pede uso do Claude na construção, não na execução |
| 2026-11-05 | PostgreSQL no Neon | Gratuito, dados compartilhados entre computadores, retoma em milissegundos (o Supabase gratuito pausa após 1 semana) |
| 2026-11-05 | Base do produto única + lentes derivadas | Consistência entre lentes e reaproveitamento em "Isso faz?" e Ideia × Código |
| 2026-11-05 | Validação de citações no backend | Combater alucinação de forma verificável |
| 2026-11-05 | Backend em camadas (api → serviços → domain/repositories/llm) e frontend por funcionalidade (seção 8) | Código previsível, testável com `FakeProvider` e fácil de achar onde mexer |
| 2026-11-05 | Documentação viva em `docs/` + `CHANGELOG.md` (seção 14) | Manter a doc junto do código e registrar a construção com o Claude para a apresentação |
| 2026-11-05 | Commits feitos pelo Roger; Claude só propõe os comandos | Preferência do Roger |
| 2026-11-05 | Chat usa base + arquivos relevantes, limitado por `CHAT_MAX_FILES` e `CHAT_CONTEXT_TOKENS` (seção 4.4) | Não estourar a cota por minuto do plano gratuito |
| 2026-11-05 | Citações no streaming por marcadores `[[caminho:Lx-Ly]]` + evento final `citations` | Manter o streaming sem exibir citação não validada |
| 2026-11-05 | Processamento em segundo plano com `projects.status` | Recarregar a página não interrompe o processamento |
| 2026-11-05 | Ollama só por troca manual no `.env` | Modelos locais erram JSON estruturado; fallback automático traria resposta pior sem aviso |
| 2026-11-05 | SQLAlchemy assíncrono + psycopg 3, sem prepared statements | Combina com SSE e chamadas paralelas; PgBouncer do Neon não suporta prepared statements |
| 2026-11-05 | Testes enxutos; integração em branch de teste do Neon | Testar só o essencial sem sobrecarregar o banco; rever se ficar lento |
| 2026-11-05 | Lista de dependências aprovadas (seção 12) | Roger delegou a escolha ao Claude; todas gratuitas e open source |
| 2026-11-05 | Evals com checagens automáticas + revisão manual | Não gastar cota com IA como juiz |
| 2026-11-05 | `projects.status` e limpeza de cache ao reprocessar, sem versionar bases | Simples; histórico de versões está em "futuro" |
| 2026-11-05 | Limites de upload no `.env` (`MAX_UPLOAD_MB`, `MAX_UNZIPPED_MB`, `MAX_FILES`) | Proteger contra zip malicioso e ajustar sem mexer no código |
| 2026-11-05 | Tokens estimados por caracteres ÷ 4 | Instantâneo, sem chamada à API, funciona com qualquer provedor |
| 2026-11-05 | Modelos simples (enums, listas, objetos) na saída estruturada | Compatível com o subconjunto de JSON Schema do Gemini e mais fácil para o Ollama |
| 2026-11-05 | Scripts npm na raiz (`npm run setup/dev/test/lint/migrate`) em vez de Makefile; suporte a Windows obrigatório | Haverá pessoas usando Windows, onde o Make não vem instalado; o Node já é pré-requisito |
| 2026-11-05 | Frontend com ESLint (não o `oxlint` que o modelo novo do Vite traz) e TypeScript fixado em `~6.0` | Seguir o padrão definido; o `typescript-eslint` ainda não suporta o TypeScript 7. Rever quando suportar |
| 2026-11-06 | Ids UUID e valores fixos como texto + CHECK (não `ENUM` nativo) | UUID não expõe contagem e pode ser gerado antes de gravar; acrescentar valor vira migração simples |
| 2026-11-06 | `product_bases` e `comparisons` com uma linha por projeto | Sem versionamento (decisão de 05/11); reprocessar substitui |
| 2026-11-06 | `/api/health` informa o banco, mas a API sobe sem ele | Quem só quer ver a interface não precisa configurar o Neon |
| 2026-11-06 | Novas tentativas também em 5xx (não só 429), via `RetryingProvider` (Decorator) | Nos testes reais o Gemini gratuito devolveu 503 "alta demanda" várias vezes; o erro costuma passar em segundos |
| 2026-11-06 | Modelo `gemini-3.5-flash` (definido no `.env`, não no código) | O 3.8 (mais novo) deu 503 seguidos; o 3.5 respondeu, com streaming e JSON validados na API real |
| 2026-11-06 | Health mostra a IA só pelo `.env`; `npm run llm:check` faz 1 chamada real, sob demanda | Não gastar cota a cada abertura da página |
| 2026-11-06 | JSON inválido não gera nova tentativa | O Gemini garante o formato; repetir só gastaria cota. Rever se o Ollama errar muito |
| 2026-11-06 | Ingestão no `POST /sources`; `/process` só faz a extração pela IA | Não havia onde guardar o arquivo original entre o envio e o processamento; a pessoa vê o tamanho do material antes de gastar cota |
| 2026-11-06 | Material acima de `MAX_CONTEXT_TOKENS` entra por prioridade, e o que fica de fora é listado na tela | Comportamento previsível, sem corte silencioso; reaproveita o ranking do chat |
| 2026-11-06 | Ideia × Código derivado da base (extração em duas etapas); tabela `comparisons` e `POST /idea-vs-code` removidos (ADR 0002) | Zero chamadas extras; "Isso faz?" e Ideia × Código leem o mesmo status e não se contradizem |
| 2026-11-06 | Lado a lado em uma chamada com saída estruturada, sem streaming | 1/3 da cota, menos risco de 429/503 na demo e mesma essência garantida pela geração |
| 2026-11-06 | Fluxo devolvido como JSON (passos, nós, arestas); o backend monta o Mermaid | Mermaid escrito pelo modelo quebra com frequência; as evidências dos passos passam pela validação |
| 2026-11-06 | `DELETE /sources` e `projects.base_outdated`; a base anterior segue visível até reprocessar | Definir o que acontece quando o material muda depois do processamento |
| 2026-11-06 | `quote` da evidência curto (~120 caracteres), conferido dentro do intervalo de linhas | Menos tokens de saída e menor risco de a base vir cortada |
| 2026-11-06 | Visão geral sob demanda (primeira abertura de cada lente) e histórico do chat limitado por `CHAT_HISTORY_TURNS` | Processamento mais rápido e custo por pergunta previsível |
| 2026-11-06 | `MAX_CONTEXT_TOKENS` vale por etapa (documentos e código) e o padrão cai para 200 mil | Na extração em duas etapas cada grupo vai numa chamada; chamadas acima do limite de tokens por minuto do plano gratuito voltam 429 sempre. Conferir o número real na Fase 4 |
| 2026-11-06 | `.env` e chaves de dentro do zip são ignorados | Não mandar segredos de quem envia o repositório para a IA |
| 2026-11-06 | Caminho repetido no projeto ganha sufixo (`README (2).md`) | Cada citação aponta para um único arquivo |
| 2026-11-06 | Zip é sempre `code`; documentos são `idea_doc` ou `transcript`; texto colado é `text` ou `transcript` | Regras simples, validadas no envio |
| 2026-11-06 | Texto extraído em thread separada (`asyncio.to_thread`); arquivos de exemplo dos testes gerados em memória | Não travar o servidor ao ler PDF/zip; nenhum binário no repositório |
| 2026-11-06 | Citação inválida é **descartada** da base (não guardada como `unverified`); o `status_detail` final informa quantas foram | A base é a verdade que todas as abas leem; no chat (Fase 5) a citação inválida aparece com o selo "não verificada" |
| 2026-11-06 | Material só de documento usa **uma** chamada (etapa b direto sobre o documento, tudo `documented_only`) | Economizar cota: a etapa (a) não acrescentaria nada |
| 2026-11-06 | Cada feature traz `promise_ref`, e o backend reconcilia o status (uma feature por promessa) | Não depender do modelo para a coerência do Ideia × Código; nenhuma promessa some |
| 2026-11-06 | Status do processamento por SSE lendo o banco a cada 1s, com sessão curta por leitura | Recarregar a página não perde nada; nenhuma conexão fica presa enquanto espera |
| 2026-11-06 | Visão geral por SSE, nos mesmos eventos do chat (`delta`, `citations`, `done`, `error`); o cache é devolvido pelos mesmos eventos | Texto aparece aos poucos na primeira geração; o frontend trata os dois casos com um código só |
| 2026-11-06 | Visão geral usa só a base (sem arquivos) | Barata e previsível; a lente técnica cita pelas evidências da base |
| 2026-11-06 | Marcador `[[caminho:Lx-Ly]]` válido = arquivo existe no projeto e as linhas existem | O marcador não leva trecho (texto mais limpo, menos tokens); pega arquivo inventado e linha fora do arquivo |
| 2026-11-06 | Tarefas `overview.md` e `chat.md` na lista de prompts; lente cliente sem marcadores de citação | Faltavam prompts de tarefa para esses casos; citação técnica não serve ao cliente final |
| 2026-11-06 | Nova rota `GET /conversations/{id}` | O chat precisa sobreviver a um recarregamento da página |
| 2026-11-06 | `created_at` das mensagens preenchido pela aplicação | `now()` é fixo dentro da transação; a ordem do histórico não pode depender de empate |
| 2026-11-06 | `remark-gfm` no frontend | A lente técnica usa tabelas; sem ele elas aparecem como texto cru |
| 2026-11-06 | Abas das Fases 7 a 9 visíveis e desativadas ("chega na Fase N") | A estrutura final do produto já aparece na tela |
| 2026-11-06 | Lente ativa e id da conversa no `localStorage` | Trocar de aba ou recarregar a página não perde o contexto |
| 2026-11-06 | Testes do frontend só em funções puras (SSE, marcadores, montagem da resposta), sem `jsdom` | Testar o que é crítico na demo sem dependência extra; telas conferidas no navegador |
| 2026-11-06 | Citações divididas entre `shared/ui/AnswerMarkdown`, `features/citations` e a página | Visão geral e chat usam citações sem uma feature importar outra (seção 8.3) |
| 2026-11-06 | Visão geral e status do processamento com o `streamedQuery` do TanStack Query | Streaming com cache por projeto e lente sem estado manual |
| 2026-11-06 | Veredito do "Isso faz?" sai do status da base; "sim" sem funcionalidade na base exige evidência válida no código; correções vêm com `adjusted` e justificativa tirada da base | "Isso faz?" e Ideia × Código nunca se contradizem |
| 2026-11-06 | "Isso faz?" responde na lente ativa (só o tom da justificativa muda); o lado a lado ignora a lente ativa | O veredito é um fato; o lado a lado já mostra as três lentes |
| 2026-11-06 | Resultados do lado a lado e do "Isso faz?" não são gravados | Sem tabela nova; o plano não pede histórico |
| 2026-11-06 | Extração com ~56 mil tokens de código passou sem 429 no `gemini-3.5-flash` | Primeiro teste real; o limite de 200 mil por etapa segue sem teste num repositório desse tamanho |

---

## 14. Documentação viva

Toda fase termina com a doc atualizada **no mesmo commit** do código. Docs técnicas em português do Brasil.

| Doc | Conteúdo | Quando criar / atualizar |
|---|---|---|
| `README.md` | Como rodar do zero em outro computador | Fase 0; sempre que mudar comando, variável ou pré-requisito |
| `CHANGELOG.md` | O que entrou em cada fase (formato Keep a Changelog) | Ao fechar cada fase |
| `docs/README.md` | Índice da pasta `docs/` | Ao criar uma doc nova |
| `docs/architecture.md` | Visão das camadas, pipeline e diagramas Mermaid | Fase 0; quando mudar módulo ou fluxo |
| `docs/adr/NNNN-titulo.md` | Uma decisão técnica relevante por arquivo (contexto, opções, decisão, consequências) | Sempre que uma decisão entrar na seção 13 e merecer explicação |
| `docs/data-model.md` | Tabelas, diagrama ER em Mermaid, formato do JSONB da base | Fase 1; a cada migração |
| `docs/llm.md` | Provedores, modelos, limites do plano gratuito, estratégia de cache e cota | Fase 2; quando mudar provedor ou modelo |
| `docs/ingestion.md` | Formatos aceitos, filtros, limites, formato com linhas numeradas | Fase 3 |
| `docs/api-events.md` | Contrato dos eventos SSE (nome, payload, ordem). O resto da API está no `/docs` do FastAPI | Fases 4 e 5; a cada evento novo |
| `docs/prompts.md` | Histórico dos prompts: o que mudou, por quê e resultado do eval | Fase 5 em diante; a cada ajuste de prompt |
| `docs/evals/AAAA-MM-DD.md` | Resultado de cada rodada do conjunto de avaliação | Fase 11 (e quando mexer em prompt) |
| `docs/runbook.md` | Problemas comuns e solução (429, Neon dormindo, Ollama, CORS) | Sempre que um problema tomar mais de 10 minutos |
| `docs/demo-script.md` | Roteiro da apresentação, perguntas e respostas esperadas | Fase 10 |
| `docs/devlog.md` | Diário da construção com o Claude Code: o que foi pedido, o que saiu, o que foi corrigido | Ao fim de cada sessão de trabalho. Vira material da apresentação |

---

## 15. Pontos em aberto

Nenhum no momento. Todos os pontos levantados em 05/11/2026 foram decididos e estão na seção 13.
Quando surgir uma dúvida que dependa do Roger, listar aqui com a recomendação do Claude; ao decidir, mover para a seção 13.

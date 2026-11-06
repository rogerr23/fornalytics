# Arquitetura

Visão de como o Fornalytics é organizado. As regras completas estão na seção 8 do `CLAUDE.md`; aqui fica o mapa.

## Pipeline do produto

```mermaid
flowchart LR
    U[Upload<br/>zip, pdf, docx, md, txt, texto] --> I[Ingestão no envio<br/>texto com linhas numeradas,<br/>resumo e corte por prioridade]
    I --> P[Etapa a: promessas<br/>do documento da ideia]
    P --> E[Etapa b: base do código<br/>status de cada promessa]
    I --> E
    E --> DB[(PostgreSQL<br/>Neon)]
    DB --> L[Lentes<br/>visão geral, chat, lado a lado,<br/>Isso faz?, fluxo]
    DB --> IC[Ideia × Código<br/>agrupa a base, sem IA]
    L --> C[Validação de citações]
    C --> F[Frontend]
    IC --> F
```

## Camadas do backend

```mermaid
flowchart TD
    R[api/routers<br/>finos, sem regra de negócio] --> S[Serviços<br/>ingestion, extraction, lenses]
    S --> D[domain<br/>modelos Pydantic puros]
    S --> RP[db/repositories<br/>único lugar com ORM]
    S --> LLM[llm<br/>só pela interface LLMProvider]
    RP --> D
```

- Dependências sempre de cima para baixo; `domain/` não importa nada do projeto.
- Serviços recebem dependências pelo construtor (injeção via `api/deps.py`).
- Erros esperados são `AppError` (`core/errors.py`), convertidos em HTTP num handler único.
- Só `core/config.py` lê variáveis de ambiente.

## Processamento da base (Fase 4)

```mermaid
sequenceDiagram
    participant F as Frontend
    participant API as POST /process
    participant R as ProcessingRunner (tarefa em segundo plano)
    participant IA as LLMProvider
    participant DB as Banco
    F->>API: processar
    API->>DB: status = processing (UPDATE condicional)
    API-->>F: 202
    API->>R: submit(projeto)
    F->>DB: GET /status (SSE, lê o status a cada 1s)
    R->>IA: etapa a: promessas (se houver documento)
    R->>IA: etapa b: base (recebe as promessas)
    R->>R: reconcilia status e confere citações
    R->>DB: base + limpa lens_cache + ready (uma transação)
    DB-->>F: evento status: ready
```

- `extraction/extractor.py` fala com a IA e não toca o banco; `extraction/reconcile.py` é puro; `extraction/service.py` grava; `extraction/runner.py` cuida da tarefa e dos erros.
- Material só de código ou só de documento usa **uma** chamada; ideia + código usa duas.

## Lentes (Fase 5)

- `lenses/context.py` (puro) monta o que vai ao modelo:
  - visão geral: só a base;
  - chat: base, arquivos relevantes (palavras da pergunta no caminho e no conteúdo, mais os arquivos citados nas evidências ligadas à pergunta) e as últimas `CHAT_HISTORY_TURNS` trocas.
- `lenses/overview.py` e `lenses/chat.py` têm duas partes:
  - `prepare` faz as checagens que viram HTTP comum (404, 409);
  - `answer` emite eventos de domínio (`TextDelta`, `CitationsChecked`...), que o router converte em SSE (`api/sse.py`).
- O trabalho durante o stream usa sessões curtas (`SessionFactory`), como o processamento em segundo plano.
- `citations/markers.py` acha e confere os marcadores `[[caminho:Lx-Ly]]` ao fim de cada resposta.

## Lado a lado e "Isso faz?" (Fase 7)

- As duas funções usam o mesmo contexto do chat (base e arquivos relevantes, em `lenses/answer.load_question_context`), fazem **uma** chamada `generate_json` e respondem em JSON, sem streaming.
- **Lado a lado** (`lenses/compare.py`): o prompt traz as três lentes de uma vez (`PromptBuilder.build_for_lenses`). Os marcadores de cada resposta são conferidos como no chat.
- **"Isso faz?"** (`lenses/does_it.py` e `lenses/verdict.py`, regra pura): as evidências passam pelo validador forte, como as da base. O veredito sai do status da funcionalidade na base:

  | Status na base | Veredito |
  |---|---|
  | `implemented` ou `undocumented` | Sim |
  | `partial` | Parcialmente |
  | `documented_only` | Não |

  - Sem funcionalidade correspondente na base, "sim" ou "parcialmente" só valem com evidência válida no código.
  - Quando o backend corrige o modelo, a resposta vem com `adjusted: true` e uma justificativa tirada da própria base.
  - É o mesmo status que o Ideia × Código agrupa, então as duas abas nunca se contradizem.
- Os resultados não ficam salvos: o histórico existe só na tela, enquanto ela estiver aberta.

## Frontend

- `app/`: rotas, layout e providers (TanStack Query e lente ativa).
- `pages/`: telas, só compõem features.
- `features/<nome>/`: uma pasta por funcionalidade (`api.ts`, `hooks/`, `components/`, `types.ts`), sem importar outra feature.
- `shared/`: cliente da API, leitor de SSE, componentes genéricos e utilitários.
- Em desenvolvimento, o Vite encaminha `/api` para `localhost:8000` (sem CORS).

### Rotas

| Rota | Página | Features usadas |
|---|---|---|
| `/` | `ProjectsPage` | `projects`, `health` |
| `/projects/new` e `/projects/:id/material` | `NewProjectPage` | `projects`, `upload`, `processing` |
| `/projects/:id/processing` | `ProcessingPage` | `processing` |
| `/projects/:id?tab=overview\|chat\|compare\|does-it` | `ProjectPage` | `lens`, `overview`, `chat`, `compare`, `does-it`, `citations`, `processing` |

### Streaming

- `shared/api/sse.ts` lê SSE com `fetch` (sem biblioteca). O `SseParser` junta eventos cortados entre pedaços e ignora `: ping`.
- **Status do processamento** e **visão geral** usam o `streamedQuery` do TanStack Query:
  - os eventos vão sendo somados num estado (`reducer`);
  - a visão geral fica em cache por projeto e lente (`staleTime: Infinity`), então trocar de lente e voltar não chama a IA.
- **Chat:** uma *mutation* lê o stream e mostra a resposta parcial. No `done`, recarrega a conversa do servidor, que já tem a resposta salva com as citações. O id da conversa fica no `localStorage`, por projeto.

### Citações na tela

As features não importam umas às outras (seção 8.3 do `CLAUDE.md`). Por isso, as citações ficam divididas em três partes:

```mermaid
flowchart LR
    O[overview / chat] -->|texto + citations| AM[shared/ui/AnswerMarkdown]
    AM -->|clique numa citação válida| P[ProjectPage]
    P -->|citation| CV[features/citations/CitationViewer]
    CV -->|GET /files?path=| API[(API)]
```

- `shared/lib/citations.ts` troca cada `[[caminho:Lx-Ly]]` por um link `cite:N` no Markdown.
- `AnswerMarkdown` desenha o chip: cinza enquanto o evento `citations` não chega, clicável quando é válida, riscado com "não verificada" quando não confere.

## O que já existe

| Parte | Status | Fase |
|---|---|---|
| `create_app()`, configurações, erros, logging | ✅ | 0 |
| `GET /api/health` (API, banco e IA) | ✅ | 0, 1 e 2 |
| Frontend com rotas, TanStack Query e Tailwind | ✅ | 0 |
| Banco: sessão assíncrona, 8 tabelas, migração inicial, status no health | ✅ | 1 |
| Provedores de IA (Gemini, Ollama, Fake) com novas tentativas | ✅ | 2 |
| Projetos (criar, listar, detalhar) e ingestão no envio: extratores, filtros, limites, corte por prioridade | ✅ | 3 |
| Base do produto: extração em duas etapas, reconciliação, validação de citações, processamento em segundo plano e status por SSE | ✅ | 4 |
| Lentes: visão geral por lente (cache) e chat com streaming, contexto selecionado e citações por marcador | ✅ | 5 |
| Telas do MVP: projetos, material com resumo da ingestão, progresso por SSE, projeto com seletor de lente, visão geral, chat e visualizador de citações | ✅ | 6 |
| Lado a lado (uma chamada para as 3 lentes) e "Isso faz?" com veredito coerente com a base | ✅ | 7 |
| Ideia × Código (agrupa a base por status) | ⏳ | 8 |
| Fluxo (JSON → Mermaid montado no backend) | ⏳ | 9 |

# Eventos SSE da API

Contrato dos Server-Sent Events. O resto da API está documentado no `/docs` do FastAPI (`http://localhost:8000/docs`).

Formato de cada evento, como no padrão SSE:

```
event: <nome>
data: <json em uma linha>

```

Linhas que começam com `:` (ex.: `: ping`) são comentários: mantêm a conexão viva e devem ser ignoradas pelo cliente.

## `GET /api/projects/{id}/status`

Acompanha o processamento iniciado por `POST /api/projects/{id}/process`. Lê `projects.status` no banco, então **recarregar a página não perde nada**: basta abrir o stream de novo.

| Evento | Quando | `data` |
|---|---|---|
| `status` | Logo ao conectar (estado atual) e a cada mudança de `status` ou `status_detail` | `{"status": "processing", "status_detail": "Montando a base a partir do código (etapa 2 de 2)", "base_outdated": false}` |

- `status`: `draft`, `processing`, `ready` ou `failed`.
- O stream **termina sozinho** depois do primeiro evento em que `status` não é `processing`. Se o projeto não está processando ao conectar, chega um evento só.
- Sem mudança por 15s, o servidor manda `: ping`.
- O stream é encerrado depois de 15 minutos, por segurança. O cliente pode reconectar.
- Projeto inexistente: `404` comum (JSON `{"detail": "..."}`), antes de abrir o stream.

### Textos de `status_detail` durante o processamento

| Material | Sequência |
|---|---|
| Ideia + código | `Na fila para processar` → `Lendo as promessas do documento da ideia (etapa 1 de 2)` → `Montando a base a partir do código (etapa 2 de 2)` → `Conferindo as citações` |
| Só código | `Na fila…` → `Montando a base a partir do código (etapa 1 de 1)` → `Conferindo as citações` |
| Só documento | `Na fila…` → `Montando a base a partir do documento da ideia (etapa 1 de 1)` → `Conferindo as citações` |

No fim:
- `ready`: `Base pronta: N funcionalidades.`, acrescido de quantas citações foram descartadas e quantos arquivos ficaram fora do limite, quando houver.
- `failed`: a mensagem amigável do erro (ex.: limite gratuito da IA, alta demanda, resposta fora do formato) ou o aviso de que o servidor reiniciou durante o processamento.

### Exemplo

```
event: status
data: {"status":"processing","status_detail":"Lendo as promessas do documento da ideia (etapa 1 de 2)","base_outdated":false}

: ping

event: status
data: {"status":"ready","status_detail":"Base pronta: 26 funcionalidades.","base_outdated":false}

```

## Respostas das lentes: `GET /api/projects/{id}/overview?lens=` e `POST /api/projects/{id}/chat`

As duas rotas usam os mesmos eventos. O frontend lê os dois casos com o mesmo código.

| Evento | Quando | `data` |
|---|---|---|
| `conversation` | Só no chat, primeiro evento | `{"conversation_id": "uuid"}`: guarde para as próximas perguntas |
| `delta` | Cada pedaço do texto, na ordem | `{"text": "..."}` |
| `citations` | Depois do último `delta` | `{"citations": [{"marker": "[[src/a.py:L10-L20]]", "path": "src/a.py", "line_start": 10, "line_end": 20, "valid": true, "problem": null}]}` |
| `done` | Fim normal | `{"cached": false, "message_id": null}` (`cached` só na visão geral; `message_id` só no chat) |
| `error` | A IA falhou com o stream já aberto (cota, alta demanda, resposta vazia) | `{"message": "texto amigável"}`. É o último evento: não vem `citations` nem `done` |

**Citações no texto:** o modelo escreve marcadores `[[caminho:L10-L20]]` ou `[[caminho:L10]]`. O texto chega como está; no evento `citations`, cada marcador traz `valid`. O frontend troca o marcador válido por um link (abre `GET /files?path=`) e o inválido por um selo "não verificada". `problem`: `file_not_found` ou `lines_out_of_range`.

Um marcador é **válido** quando o arquivo existe no projeto e as linhas existem nele. O marcador não tem trecho, então essa conferência é mais fraca que a da base (que confere o trecho).

**Visão geral:**
- `lens`: `cliente`, `nao_tecnico` ou `tecnico`.
- Primeira abertura de cada lente: o texto vem por streaming e é salvo em cache.
- Depois: um único `delta` com o texto do cache e `done.cached = true`. As citações são conferidas de novo a cada abertura.
- Resposta com erro não vai para o cache.

**Chat:**
- Corpo: `{"lens": "tecnico", "question": "...", "conversation_id": null}` (pergunta com até 2000 caracteres).
- A pergunta é gravada antes da resposta; a resposta, com as citações, só ao fim. Se der `error`, a pergunta fica sem resposta e não entra no histórico enviado à IA.

**Erros antes do stream** (resposta JSON comum, sem SSE):

| Código | Quando |
|---|---|
| 404 | Projeto ou conversa inexistente |
| 409 | O projeto ainda não tem base: processe antes |
| 422 | Lente inválida ou pergunta vazia ou longa demais |
| 503 | IA não configurada no `.env` |

### Exemplo (chat)

```
event: conversation
data: {"conversation_id":"6f1c..."}

event: delta
data: {"text":"A validação fica em "}

event: delta
data: {"text":"[[backend/app/citations/validator.py:L72-L86]]."}

event: citations
data: {"citations":[{"marker":"[[backend/app/citations/validator.py:L72-L86]]","path":"backend/app/citations/validator.py","line_start":72,"line_end":86,"valid":true,"problem":null}]}

event: done
data: {"cached":false,"message_id":"9a2e..."}

```

`GET /api/projects/{id}/conversations/{conversation_id}` (JSON) devolve as mensagens de uma conversa, com as citações, para remontar o chat depois de recarregar a página.

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

## Próximos eventos

O chat (Fase 5) vai transmitir o texto e terminar com um evento `citations`. Ele será documentado aqui.

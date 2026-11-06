# Modelo de dados

PostgreSQL no Neon, acessado com SQLAlchemy 2 assíncrono + psycopg 3. Migrações com Alembic.
Código: `backend/app/db/models/` (tabelas) e `backend/app/domain/enums.py` (valores fixos).

## Diagrama

```mermaid
erDiagram
    projects ||--o{ sources : tem
    sources ||--o{ source_files : contem
    projects ||--o| product_bases : tem
    projects ||--o{ lens_cache : guarda
    projects ||--o| comparisons : tem
    product_bases ||--o{ comparisons : origina
    projects ||--o{ conversations : tem
    conversations ||--o{ messages : contem

    projects {
        uuid id PK
        varchar name
        varchar status
        text status_detail
        timestamptz created_at
    }
    sources {
        uuid id PK
        uuid project_id FK
        varchar type
        varchar filename
        timestamptz created_at
    }
    source_files {
        uuid id PK
        uuid source_id FK
        text path
        text content
        int token_estimate
    }
    product_bases {
        uuid id PK
        uuid project_id FK "único"
        jsonb data
        varchar provider
        varchar model
        timestamptz created_at
    }
    lens_cache {
        uuid project_id PK
        varchar lens PK
        varchar kind PK
        text content
        timestamptz created_at
    }
    comparisons {
        uuid id PK
        uuid project_id FK "único"
        uuid product_base_id FK
        jsonb data
        timestamptz created_at
    }
    conversations {
        uuid id PK
        uuid project_id FK
        timestamptz created_at
    }
    messages {
        uuid id PK
        uuid conversation_id FK
        varchar lens
        varchar role
        text content
        jsonb citations
        timestamptz created_at
    }
```

## Tabelas

| Tabela | Para quê | Observações |
|---|---|---|
| `projects` | Um produto analisado | `status` acompanha o processamento (Fase 4) |
| `sources` | Cada arquivo enviado ou texto colado | `filename` vazio para texto colado |
| `source_files` | Texto extraído de cada arquivo (um zip gera vários) | Único por `source_id` + `path`; o arquivo original não é guardado |
| `product_bases` | A base do produto em JSON | **Uma por projeto**: reprocessar substitui |
| `lens_cache` | Saídas em cache por lente (hoje só a visão geral) | Chave: projeto + lente + tipo |
| `comparisons` | Resultado do Ideia × Código | **Uma por projeto**; aponta para a base que a gerou |
| `conversations` / `messages` | Histórico do chat | `citations` guarda as citações já validadas |

## Valores aceitos

Guardados como texto, com uma regra (`CHECK`) no banco que recusa qualquer outro valor.

| Campo | Valores |
|---|---|
| `projects.status` | `draft`, `processing`, `ready`, `failed` |
| `sources.type` | `code`, `idea_doc`, `transcript`, `text` |
| `lens_cache.lens`, `messages.lens` | `cliente`, `nao_tecnico`, `tecnico` |
| `lens_cache.kind` | `overview` |
| `messages.role` | `user`, `assistant` |

## Regras

- **Ids** são UUID gerados pela aplicação.
- **Datas** com fuso horário, preenchidas pelo banco (`now()`).
- **Apagar um projeto apaga tudo que pertence a ele** (`ON DELETE CASCADE` em todas as chaves estrangeiras).
- **Reprocessar um projeto** apaga `lens_cache` e `comparisons` dele na mesma transação que grava a nova base (Fase 4).
- O formato dos campos `jsonb` é definido pelos modelos Pydantic de `app/domain/` (Fase 4 em diante).

## Conexões

| Variável | Uso |
|---|---|
| `DATABASE_URL` | Conexão **pooled** (endereço com `-pooler`), usada pela aplicação |
| `DATABASE_URL_DIRECT` | Conexão direta, usada pelo Alembic |
| `TEST_DATABASE_URL` | Branch `test` do Neon, usado só pelos testes de integração |

As URLs podem ser coladas como o Neon entrega (`postgresql://...`); o código escolhe o driver sozinho.
A conexão pooled não aceita *prepared statements*, por isso o engine usa `prepare_threshold=None`.

## Como mudar o esquema

1. Altere ou crie o model em `backend/app/db/models/` (e registre-o em `models/__init__.py`).
2. Gere a migração:
   ```bash
   npm run migration:new -- -m "descricao curta em ingles"
   ```
3. **Revise** o arquivo gerado em `backend/alembic/versions/` antes de aplicar.
4. Aplique:
   ```bash
   npm run migrate
   ```
5. Atualize esta página no mesmo commit.

Nunca altere tabelas manualmente no painel do Neon.

# Ingestão

Como o material enviado vira texto no banco. Acontece **no envio** de cada fonte (`POST /api/projects/{id}/sources`), sem IA. Código em `backend/app/ingestion/`.

## Formatos e tipos

| Formato | Extrator | `type` aceito |
|---|---|---|
| `.zip` (repositório) | `zipfile` (em memória, nunca no disco) | `code` |
| Link de repositório público do GitHub (`url`) | baixado como `.zip` e lido pelo mesmo extrator (ver [Repositório do GitHub](#repositório-do-github)) | `code` |
| `.pdf` | `pdfplumber`, com uma linha `--- página N ---` antes de cada página | `idea_doc`, `transcript` |
| `.docx` | `python-docx` (parágrafos e tabelas, células separadas por ` \| `) | `idea_doc`, `transcript` |
| `.md`, `.txt` | leitura direta | `idea_doc`, `transcript` |
| Texto colado (`title` + `content`) | leitura direta, salvo como `<title>.txt` | `text`, `transcript` |

- Texto que não é UTF-8 é lido como Latin-1. Quebras de linha viram `\n`.
- PDF escaneado (sem texto selecionável) é recusado com explicação.
- Arquivo de texto ou texto colado acima de 200 KB é recusado.
- Acrescentar um formato: criar um extrator em `extractors/` com `extensions` e `extract()` e registrá-lo em `extractors/__init__.py`.

## Envio pela API

Formulário `multipart/form-data`:

| Campo | Quando |
|---|---|
| `type` | Sempre |
| `file` | Para enviar arquivo |
| `url` | Para importar um repositório público do GitHub (sem `file`; `type` sempre `code`) |
| `title`, `content` | Para colar texto (sem `file` nem `url`) |

Para testar sem frontend: `npm run dev`, abra http://localhost:8000/docs, crie um projeto em `POST /api/projects` e use **Try it out** em `POST /api/projects/{project_id}/sources`.

### Resumo devolvido

| Campo | O que é |
|---|---|
| `files` | Arquivos que entraram, com tokens estimados |
| `skipped` | Ignorados, agrupados por motivo, com até 5 exemplos |
| `renamed` | Caminhos que ganharam sufixo por já existirem no projeto |
| `token_estimate` | Tokens desta fonte |
| `base_outdated` | `true` se o projeto já tinha base e o material mudou |
| `limits` | Como o projeto inteiro cabe no limite, por etapa (ver abaixo) |

## Filtros (`filters.py`)

| Motivo (`reason`) | O que cai aqui |
|---|---|
| `ignored_dir` | Dentro de `node_modules`, `.git`, `dist`, `build`, `.next`, `venv`, `.venv`, `__pycache__`, `.idea`, `.vscode`, caches de ferramentas, `coverage` |
| `lockfile` | `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `uv.lock`, `poetry.lock`, `Cargo.lock` e semelhantes |
| `secret` | `.env` e `.env.*` (menos `.env.example`, `.env.sample`, `.env.template`), `.pem`, `.key`, `.p12`, `.pfx` |
| `binary` | Imagens (inclui `.svg`), fontes, mídia, compactados, documentos dentro do zip, compilados; ou bytes nulos no conteúdo |
| `minified` | `.min.js`, `.min.css`, `.map`, ou linhas com média acima de 500 caracteres |
| `too_large` | Acima de 200 KB |
| `unsafe_path` | Caminho absoluto, com `..` ou link simbólico |
| `empty` | Sem texto (ex.: `__init__.py` vazio) |

Zips baixados do GitHub vêm com uma pasta por fora (`loja-main/`); ela é removida dos caminhos.

## Limites de segurança

| Variável | Padrão | Como é conferido |
|---|---|---|
| `MAX_UPLOAD_MB` | 20 | Durante a leitura do arquivo enviado (413) |
| `MAX_UNZIPPED_MB` | 100 | Soma do tamanho **real** descompactado, não do declarado no zip (413) |
| `MAX_FILES` | 2000 | Número de arquivos no zip (413) |

Zip com senha ou corrompido, formato não suportado e tipo incompatível com o arquivo devolvem 422 com a explicação em português.

## Repositório do GitHub

Código em `ingestion/remote/github.py`. Decisão em [ADR 0003](adr/0003-importacao-por-link-do-github.md).

- **Links aceitos:** `github.com/dono/repo`, com ou sem `https://`, `www.`, `.git`, barra final, `?…` ou `#…`, e `github.com/dono/repo/tree/branch`. Sem branch, vale o branch padrão do repositório.
- **Recusados com explicação (422):** outro site, link sem o nome do repositório, página interna (`/issues`, `/blob/…`), subpasta (`/tree/main/src`) e branch com `/` no nome (não dá para separar do caminho da subpasta).
- **Download:** só o dono, o repositório e o branch saem do link. O endereço é montado no backend, sempre em `https://codeload.github.com/{dono}/{repo}/zip/{branch ou HEAD}`, e redirecionamentos não são seguidos. Assim um link nunca faz o servidor acessar outro endereço.
- **Limites:** o download é lido aos poucos e para ao passar de `MAX_UPLOAD_MB` (413). Depois, o zip passa pelo `ZipExtractor`, com os mesmos filtros, `MAX_UNZIPPED_MB` e `MAX_FILES` do envio. Tempo máximo de 120 s.
- **Nome da fonte:** `github.com/dono/repo` ou `github.com/dono/repo@branch` (campo `filename`, sem migração).
- **Erros:**

  | Situação | Resposta |
  |---|---|
  | Repositório ou branch inexistente, ou repositório privado (o GitHub responde 404 nos dois casos) | 422, "Só repositórios públicos são aceitos" |
  | GitHub limitando downloads (403/429), outro erro do GitHub, timeout ou sem internet | 502 (`SourceUnavailable`), sugerindo tentar de novo ou enviar o `.zip` |

- **O que não faz:** repositório privado (exigiria token), GitLab, subpasta e atualização automática a cada commit. Para trazer uma versão nova, remova a fonte e importe de novo.

## Prioridade e corte (`filters.path_priority`, `selection.py`, `limits.py`)

Ordem de leitura do código: **README → rotas/controllers → models/schemas → services → config → resto → testes**. Empate: o arquivo mais raso vem antes; depois, ordem alfabética.

`MAX_CONTEXT_TOKENS` (padrão 200 mil) vale **por etapa** da extração:

- **documentos** (`idea_doc`, `transcript`, `text`) → etapa (a), promessas;
- **código** → etapa (b), base.

Em cada grupo, os arquivos entram na ordem de prioridade enquanto couberem; um arquivo grande que não cabe fica de fora, e arquivos menores depois dele ainda podem entrar. O que ficou de fora aparece em `limits.<grupo>.excluded` (nunca há corte silencioso). A mesma função vai servir ao chat.

## Formato enviado à IA (`rendering.py`)

```
=== src/services/payment.ts ===
1| import ...
2| ...
```

Tokens estimados por caracteres ÷ 4 (`tokens.py`), sem chamar API.

## Caminhos repetidos

Cada caminho é único no projeto. Se uma fonte nova trouxer um caminho que já existe, ele vira `nome (2).ext` (depois `(3)`, …) e aparece em `renamed`.

## Mudança de material

Adicionar ou remover uma fonte de um projeto que já tem base marca `projects.base_outdated = true`. Enquanto o projeto estiver em `processing`, o material não pode mudar (409).

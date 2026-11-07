# 0003 — Importação de repositório público do GitHub por link

- **Data:** 2026-11-06
- **Status:** aceita

## Contexto

Para analisar um repositório, a pessoa precisava baixar o `.zip` no GitHub e enviá-lo. O Roger pediu para aceitar também o link do repositório. O documento de produto (seção 4.3) deixa para o futuro a "integração direta com GitHub/GitLab e atualização automática a cada commit". Este pedido é só a parte de importar uma vez.

## Opções consideradas

1. **Baixar o `.zip` do repositório pelo endereço público do GitHub** e reaproveitar o `ZipExtractor`.
   - Prós: nenhuma dependência nova, filtros, limites e resumo iguais aos do envio, e uma única requisição.
   - Contras: só repositórios públicos e sem escolher subpasta.
2. **API REST do GitHub arquivo por arquivo.**
   - Prós: daria para escolher subpasta.
   - Contras: centenas de requisições, limite de 60 por hora sem token e um segundo caminho de ingestão para manter.
3. **`git clone`.**
   - Contras: exige o Git no servidor, escreve no disco e não funciona igual em todos os sistemas.
4. **Integração com OAuth (repositórios privados e sincronização).**
   - Contras: fora do escopo do protótipo (seção 4.3) e exigiria guardar tokens.

## Decisão

Opção 1. Do link saem só o dono, o repositório e o branch. O backend monta o endereço em `codeload.github.com`, não segue redirecionamentos e corta o download em `MAX_UPLOAD_MB`. A fonte é gravada como `code`, com `filename` = `github.com/dono/repo[@branch]`.

## Consequências

- Repositórios open source entram com um link. É o tipo de material que podemos mandar ao plano gratuito do Gemini (seção 3 do `CLAUDE.md`).
- Como o host é fixo, o link não abre caminho para o servidor acessar endereços internos (SSRF).
- Sem migração e sem dependência nova.
- Repositórios privados, GitLab, subpastas, branches com `/` no nome e sincronização continuam em "próximos passos". Para atualizar, a pessoa remove a fonte e importa de novo.
- Repositórios grandes param no `MAX_UPLOAD_MB`, e a mensagem sugere enviar um `.zip` só com as pastas importantes.

# Diário de construção

Registro de como o Fornalytics está sendo construído com o Claude Code e o Cowork.
Uma entrada por sessão de trabalho: o que foi pedido, o que saiu, o que precisou de correção e o que se aprendeu.

---

## 2026-11-05 — Planejamento técnico

- **Pedido:** revisar o `CLAUDE.md`, levantar pontos em aberto, definir estrutura de código e documentação.
- **Resultado:** estrutura em camadas no backend e por funcionalidade no frontend (seção 8 do `CLAUDE.md`), plano de documentação viva (seção 14), 12 pontos técnicos em aberto com recomendação (seção 15) e documento de produto atualizado para a v2.
- **Próximo passo:** Roger decidir os pontos em aberto e iniciar a Fase 0.

## 2026-11-05 — Fechamento dos pontos em aberto

- **Pedido:** debater os 12 pontos técnicos da seção 15 do `CLAUDE.md`.
- **Resultado:** todos decididos e registrados na seção 13. Ajustes do Roger em relação às recomendações: limitar a quantidade de arquivos enviados no chat (`CHAT_MAX_FILES`) e manter os testes enxutos, só no essencial, cuidando para não sobrecarregar o Neon.
- **Próximo passo:** Fase 0 (base do projeto).

## 2026-11-05 — Makefile trocado por scripts npm

- **Pedido:** Roger não conhecia o Make e avisou que haverá pessoas usando Windows.
- **Resultado:** comandos do projeto passam a ser scripts npm no `package.json` da raiz; suporte a Windows virou regra (seção 9 do `CLAUDE.md`); `.gitattributes` para quebras de linha; Python instalado pelo próprio `uv`.

## 2026-11-05 — Fase 0 (base do projeto)

- **Pedido:** montar o esqueleto do projeto conforme a explicação aprovada.
- **Resultado:** scripts npm na raiz, backend FastAPI com `/api/health` e teste, frontend com Tailwind, TanStack Query e React Router mostrando o status da API. Lint, formatação, build e teste passando; tela conferida no navegador.
- **Correções no caminho:** o modelo atual do Vite trocou o ESLint pelo `oxlint` e veio com TypeScript 7, que o `typescript-eslint` ainda não suporta. Mantido o ESLint (padrão do projeto) com TypeScript fixado em 6.0.
- **Fechamento (2026-11-06):** `uv` instalado via Homebrew; `npm run setup` gerou o `backend/uv.lock`; `npm test`, `npm run lint` e `npm run dev` conferidos pelo fluxo oficial. Fase 0 concluída.
- **Observação:** `npm audit` aponta 10 vulnerabilidades moderadas no `minimatch`, usado só pelo ESLint em desenvolvimento (não vai para a aplicação). A correção automática rebaixaria o ESLint; acompanhar uma atualização do ESLint.

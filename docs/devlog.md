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

## 2026-11-06 — Fase 1 (banco de dados)

- **Pedido:** conectar o Neon, criar as tabelas e a primeira migração.
- **Resultado:** 8 tabelas criadas no Neon pela migração inicial; health e página inicial mostram "Banco: ok"; testes de banco rodam no branch `test` com rollback (nenhum dado fica) e são pulados sem a URL.
- **Ajustes no caminho:** o Neon perguntou por serviços extras (escolhido "Just Postgres") e o branch `test` vinha com apagamento automático para o dia seguinte (trocado para nunca). Na revisão da migração, o nome da restrição única composta foi corrigido e o ruff foi configurado para reconhecer o pacote `alembic`.
- **Observação:** o FastAPI avisa nos testes que prefere `httpx2` ao `httpx`; é só aviso.

## 2026-11-06 — Fase 2 (provedores de IA)

- **Pedido:** criar a camada de IA (interface, Gemini, Ollama, Fake) com tratamento do limite gratuito.
- **Resultado:** 20 testes sem rede; `llm:check` respondendo pelo Gemini; streaming e JSON estruturado validados na API real com uma pergunta do tipo "Isso faz?".
- **Descobertas no caminho:**
  - O `google-genai` instalado é a versão 3.0 (mais nova que a referência do Claude); a API foi conferida no próprio pacote antes de escrever o provedor.
  - O SDK tem novas tentativas próprias; foram desligadas para não multiplicar chamadas com as nossas.
  - Nos testes reais, o Gemini gratuito devolveu **503 "alta demanda"** várias vezes (no 3.8 e no 3.5). A política foi estendida para tentar de novo também em 5xx; depois disso o `llm:check` se recuperou sozinho de um 503.
  - Linha vazia no `.env` (ex.: `LLM_PROVIDER=`) passou a valer como "não preenchida".
- **Modelo escolhido:** `gemini-3.5-flash`.

## 2026-11-06 — Revisão do fluxo do sistema

- **Pedido:** reavaliar o fluxo de ponta a ponta antes da Fase 3 e ver as telas num protótipo.
- **Resultado:** encontrada uma contradição (o `/process` fazia a ingestão, mas o arquivo original não tinha onde ficar entre o envio e o processamento) e 6 pontos de melhoria. Um protótipo navegável das 4 telas (projetos, envio, processamento e projeto com as 6 abas) ajudou a visualizar as mudanças antes de aprovar.
- **Decisões:** ingestão no envio; corte por prioridade; Ideia × Código derivado da base, com extração em duas etapas (ADR 0002); lado a lado em uma chamada; fluxo em JSON com Mermaid montado no backend; remoção de fonte com aviso de base desatualizada; ajustes menores (trecho curto, visão geral sob demanda, histórico do chat limitado).
- **Efeito na cota:** processar + Ideia × Código cai de 3–4 para 2 chamadas; o lado a lado, de 3 para 1.
- **Próximo passo:** explicar a Fase 3, que começa pela migração que remove `comparisons` e adiciona `projects.base_outdated`.

## 2026-11-06 — Fase 3 (ingestão)

- **Pedido:** rever a Fase 3 com as docs da revisão do fluxo e executá-la, seguindo as recomendações nos pontos em aberto.
- **Resultado:** migração aplicada (sai `comparisons`, entra `base_outdated`); projetos e fontes pela API; 48 testes (43 de unidade, sem rede). Conferido com um zip real do próprio Fornalytics: 74 arquivos usados, 9 vazios, 3 lockfiles e 1 SVG ignorados, pasta de fora do zip removida, nada fora do limite. PDF, texto colado, leitura de arquivo e os erros (zip com `../`, 2001 arquivos, tipo errado) conferidos pela API; o projeto de teste foi apagado do banco principal em seguida.
- **Decisões dos pontos em aberto:** limite por etapa (documentos e código) com padrão de 200 mil tokens; `.env` de dentro do zip ignorado; caminho repetido ganha sufixo.
- **Ajuste no caminho:** quando nenhum arquivo do zip é aproveitável, a mensagem agora diz o motivo de cada ignorado (ex.: "1 caminho inseguro").
- **Observação:** os arquivos de exemplo dos testes (zip, PDF, DOCX) são gerados em memória; o PDF é montado à mão, sem biblioteca extra.

## 2026-11-06 — Fase 4 (base do produto)

- **Pedido:** explicar a Fase 4 e executá-la, com commits separados por parte.
- **Resultado:** 76 testes (67 de unidade, sem rede). Teste real no Gemini com o próprio Fornalytics (106 arquivos de código e o documento de produto como ideia): 2 chamadas em cerca de 1min35s, SSE mostrando as etapas, 26 funcionalidades e **nenhuma citação descartada**. O projeto de teste foi apagado do banco principal em seguida.
- **Decisões aprovadas:** citação inválida é descartada da base; material só de documento usa uma chamada; teste real no fim da fase.
- **Ajuste no caminho:** o teste de unidade pegou um erro na renumeração das promessas (uma promessa sem nome fazia pular um número, P1 → P3).
- **Observações:**
  - o documento de produto entrou como `fornalytics-projeto (2).md`, porque o zip já tinha um arquivo com esse nome (sufixo da Fase 3, funcionando como esperado);
  - as ideias "futuras" do documento viraram promessas `documented_only` (anotado em `docs/prompts.md` para a Fase 11);
  - o limite de 200 mil tokens por etapa ainda não foi testado num repositório desse tamanho: o teste usou cerca de 56 mil.

## 2026-11-06 — Fase 5 (lentes: visão geral e chat)

- **Pedido:** explicar a Fase 5 e executá-la com as recomendações das decisões.
- **Resultado:** 88 testes (75 de unidade). Teste real no Gemini: as visões gerais técnica (20 citações válidas) e cliente (sem jargão) saíram com tons bem diferentes; o chat técnico deu 13 citações válidas e o histórico passou entre perguntas em lentes diferentes. Projeto de teste apagado em seguida.
- **Descobertas no caminho:**
  - O teste de integração mostrou que o `now()` do Postgres é o mesmo dentro de uma transação, e a ordem das mensagens ficava aleatória. O horário passou a ser gravado pela aplicação.
  - O primeiro reprocessamento caiu em 503 três vezes seguidas e o projeto ficou `failed` com a mensagem amigável; a segunda tentativa passou. Bom sinal para a demo: o erro aparece de forma limpa.
  - Uma resposta confundiu um exemplo do documento (nota fiscal da loja de demonstração) com uma funcionalidade planejada do produto. Anotado para o eval.
  - Desta vez, o reprocessamento descartou 10 citações (na Fase 4 foram 0).

## 2026-11-06 — Fase 6 (frontend do MVP)

- **Pedido:** explicar a Fase 6 e executá-la com as recomendações (`remark-gfm`, abas futuras desativadas, lente e conversa no navegador, manter o projeto de teste).
- **Resultado:** 4 telas e 9 features no frontend; 8 testes de frontend (leitor de SSE, marcadores, montagem da resposta) somados aos 83 do backend. Jornada conferida no painel de navegador do app:
  - criar projeto;
  - enviar zip (146 arquivos, 86,6 mil tokens) e documento, com resumo;
  - processar com progresso por SSE e retomada ao recarregar;
  - erro de cota amigável e "Tentar de novo";
  - visão geral com tabela e chips de citação (válida abre o arquivo com as linhas destacadas; inválida aparece como "não verificada");
  - cache ao trocar de lente;
  - chat com selo da lente por resposta e histórico mantido ao recarregar;
  - aviso "O material mudou".
- **Cota:** o processamento real esbarrou no 429 e, no "Tentar de novo", a espera pedida foi de 52.323 segundos: **acabou a cota diária** do `gemini-3.5-flash`. A visão geral e o chat foram conferidos com um provedor simulado num script local, fora do repositório (o conteúdo real do Gemini já tinha sido validado na Fase 5). Registrado em `docs/runbook.md`.
- **Corrigido no caminho:**
  - a mensagem de cota passou a mostrar minutos ou horas e a dizer quando é o limite diário;
  - as sugestões do chat não apareciam numa conversa nova (consulta desativada conta como `isPending` no TanStack Query; trocado por `isLoading`);
  - a pergunta aparecia duas vezes durante o streaming;
  - o selo da lente esticava na largura toda.
- **Projeto de teste:** "Fornalytics (teste)" ficou no banco com o zip e o documento, em rascunho. Falta clicar em **Processar** quando a cota voltar.
- **Observação:** o build avisa que o pacote passa de 500 KB (por causa do Markdown). Não atrapalha a demo; dividir o código fica para a Fase 11, se fizer falta.

## 2026-11-06 — Fase 7 (lado a lado e "Isso faz?")

- **Pedido:** explicar a Fase 7 e executá-la com as recomendações (veredito pela base, "Isso faz?" na lente ativa, sem gravar resultados, teste real com outro modelo se houvesse cota).
- **Resultado:** 103 testes no backend e 10 no frontend. As duas abas foram conferidas no navegador com respostas simuladas:
  - três colunas, com a citação técnica clicável;
  - um "Não" do modelo para uma funcionalidade implementada foi corrigido para "Sim", com o aviso de ajuste e a evidência da base.
- **Teste real:** não foi possível hoje.
  - `gemini-3.7-flash`: 504 e 503 seguidos.
  - `gemini-3.6-flash`: passou no `llm:check`, mas esgotou o limite diário na etapa 2 do processamento (o modelo foi passado só no comando, sem mexer no `.env`).
  - A mensagem nova de cota apareceu na tela como esperado ("cerca de 14 horas").
  - O projeto de teste voltou para rascunho.
- **Ajustes no caminho:**
  - trocar de aba apagava as respostas do lado a lado e do "Isso faz?" (agora ficam no cache do TanStack Query durante a sessão);
  - o status `implemented` aparecia como "prometida e implementada" até em projetos só de código (agora: "implementada no código").
- **Pendente:** teste real das duas abas quando a cota voltar (roteiro em `docs/prompts.md`, v3).

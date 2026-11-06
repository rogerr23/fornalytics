# 0002 — Ideia × Código derivado da base do produto

- **Data:** 2026-11-06
- **Status:** aceita

## Contexto

O plano original extraía as funcionalidades do documento da ideia e do código **separadamente** e depois fazia um **cruzamento** com a IA, guardando o resultado na tabela `comparisons` (rota `POST /idea-vs-code`).

Ao revisar o fluxo, ficaram claros três problemas:

- A `ProductBase` já tem `features[].status` com `implemented`, `partial`, `documented_only` e `undocumented`, que são exatamente as colunas do Ideia × Código. A informação ficaria duplicada.
- O cruzamento custava 2 ou 3 chamadas a mais no plano gratuito, que tem limite por minuto e oscila (503).
- O "Isso faz?" (que lê a base) e o Ideia × Código (que lia `comparisons`) poderiam se contradizer na demo.

## Opções consideradas

1. **Manter extrações separadas + cruzamento** — prós: cada etapa é simples. Contras: mais chamadas, mais uma tabela e risco de contradição entre as abas.
2. **Uma única extração lendo ideia e código juntos** — prós: uma chamada. Contras: o modelo tende a misturar o que foi prometido com o que existe; difícil de depurar.
3. **Extração em duas etapas encadeadas** — (a) lista de promessas a partir do documento; (b) base do código recebendo essa lista e marcando o status de cada promessa. Prós: 2 chamadas no total, status único, cada etapa depurável. Contras: o processamento fica sequencial e a qualidade do Ideia × Código depende da etapa (b).

## Decisão

Opção 3. O Ideia × Código passa a ser uma visão da base, agrupada por status, sem chamada à IA. A tabela `comparisons` e o `POST /idea-vs-code` saem; fica só `GET /projects/{id}/idea-vs-code`.

## Consequências

- O Ideia × Código e o "Isso faz?" leem o mesmo status e não podem se contradizer.
- A Fase 8 vira uma rota de leitura e a tela de três colunas.
- Nova migração no início da Fase 3: remove `comparisons` (e o model `Comparison`) e adiciona `projects.base_outdated`.
- Prompts: entra `extraction_idea.md`; sai `idea_vs_code.md`.
- Sem documento da ideia, a etapa (a) é pulada e a aba pede o documento. Sem código, a base descreve a ideia e tudo fica `documented_only`.
- Risco: um erro de marcação na etapa (b) aparece nas duas abas ao mesmo tempo. Mitigação: o repositório de demo com lacunas propositais (Fase 10) e o conjunto de avaliação (Fase 11), que confere o status esperado de cada funcionalidade.

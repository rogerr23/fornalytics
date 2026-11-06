# Prompts

Os prompts ficam em `backend/app/prompts/*.md` e são montados pelo `PromptBuilder` (`prompts/builder.py`) sempre na ordem **base + lente + tarefa**, separados por `---`. A extração da base não usa lente.

Este arquivo registra o que mudou em cada prompt, por quê e o resultado.

## v1 (2026-11-06), Fase 4: extração da base

| Arquivo | Papel |
|---|---|
| `base.md` | Regras de toda resposta: só o material, "não encontrei no material", nunca inventar arquivo ou linha, explicação do formato com linhas numeradas, português do Brasil |
| `extraction_idea.md` | Etapa (a): lista de promessas (funcionalidades prometidas) do documento da ideia, com até 2 evidências cada |
| `extraction.md` | Etapa (b): a `ProductBase`, com o `MODO` informado na mensagem (`codigo_com_promessas`, `so_codigo`, `so_ideia`) |

**Escolhas e motivos:**
- **Limites de quantidade** (30 promessas, 30 features, 6 fluxos, 15 regras, até 3 evidências por item) para a base não vir cortada.
- **Trecho curto e literal** (até 120 caracteres), sem o número da linha. O validador confere esse trecho dentro do intervalo citado.
- **`promise_ref`** em cada feature: o backend usa esse id para garantir uma feature por promessa e juntar a evidência do documento à do código (`extraction/reconcile.py`). O prompt pede, mas o backend não confia: promessa esquecida vira `documented_only`, referência desconhecida vira `undocumented`.
- **"Na dúvida entre implemented e partial, escolha partial"**: errar para menos é melhor na demo do Ideia × Código.
- As promessas são **renumeradas** (`P1…Pn`) pelo backend antes da etapa (b).

**Resultado do primeiro teste real** (`gemini-3.5-flash`, repositório do próprio Fornalytics: 106 arquivos, cerca de 56 mil tokens de código, mais o documento de produto como ideia):
- 2 chamadas em cerca de 1min35s, sem 429/503;
- 26 funcionalidades, **0 citações descartadas**;
- 5 promessas encontradas no código (1 `implemented`, 4 `partial`), 15 `documented_only` e 6 `undocumented` coerentes (ex.: remoção de fonte, retry da IA).

**Pontos para a Fase 11 (eval):** o documento de produto lista as ideias "futuras" (seção 4.3), e a etapa (a) as tratou como promessas (`documented_only`). Isso está de acordo com o prompt atual ("inclua o que foi prometido para uma versão futura"), mas pode poluir a coluna ⚠️ quando o escopo misturar MVP e futuro. Rever com o escopo da demo.

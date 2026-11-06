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

## v2 (2026-11-06), Fase 5: lentes, visão geral e chat

| Arquivo | Papel |
|---|---|
| `lens_cliente.md` | Valor e benefícios, sem jargão, frases curtas; o que foi só planejado aparece como "planejado"; **sem marcadores de citação** |
| `lens_nao_tecnico.md` | Como funciona na prática, analogias, fluxos numerados, regras de negócio em linguagem simples; poucas citações |
| `lens_tecnico.md` | Arquitetura, arquivos, funções e integrações com nomes exatos; **sempre** cita arquivo e linhas |
| `overview.md` | Visão geral em 5 seções (o que é, o que faz, como funciona, regras, o que ainda não existe), de 250 a 500 palavras, a partir só da base |
| `chat.md` | Resposta direta primeiro, "não encontrei no material", aviso para o que foi prometido e não implementado, até 250 palavras |

O formato dos marcadores (`[[caminho:L10-L20]]`) fica nas tarefas (`overview.md`, `chat.md`), não no `base.md`, porque a extração não usa marcadores.

**Resultado do teste real** (`gemini-3.5-flash`, mesmo material da Fase 4):
- Visão geral técnica: 549 palavras (um pouco acima do limite), **20 citações, todas válidas**, conferidas por amostragem.
- Visão geral cliente: 436 palavras, sem jargão, sem citações, com o planejado separado do que existe. Os tons das duas lentes ficaram bem diferentes.
- Chat técnico ("Como funciona a validação de citações?"): 193 palavras, 13 citações válidas, todas no arquivo certo.
- Chat cliente ("O produto emite nota fiscal?"): respondeu "Não", mas disse que a nota fiscal "foi prevista no escopo". Na verdade, o documento de produto só cita a nota fiscal como exemplo da loja de demonstração. **Confusão de contexto**: entra no eval da Fase 11 (pergunta de controle sobre algo citado só como exemplo).
- Na mesma rodada, o reprocessamento descartou 10 citações (na Fase 4 tinham sido 0). O validador funcionou, mas vale medir no eval se o descarte está alto.

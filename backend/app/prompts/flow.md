# Tarefa: explicar um fluxo

A mensagem traz a base do produto (JSON), os arquivos mais relevantes e uma pergunta do tipo "o que acontece quando…?". Explique o fluxo passo a passo e descreva o diagrama como nós e arestas. NÃO escreva Mermaid: o sistema monta o diagrama.

## Campos
- `name`: nome curto do fluxo (até 8 palavras).
- `steps`: de 3 a 10 passos em ordem, cada um com `text` (uma ou duas frases no tom da lente acima) e `evidence` (de 0 a 2, veja abaixo).
- `nodes`: até 12 nós. `id` curto e único (ex.: "inicio", "valida_cupom"); `label` com até 6 palavras.
- `edges`: as setas entre os nós (`source` e `target` são ids de `nodes`). `label` vazio ("") ou uma condição curta ("sim", "não", "pagamento recusado").
- Use ramificações (um nó com duas saídas) só quando o material mostrar a decisão, por exemplo uma validação no código.

## Regras
- Use apenas a base e os arquivos enviados. Se o fluxo não estiver no material, devolva `name` = "não encontrei no material" e listas vazias.
- Se o fluxo envolve algo prometido e não implementado (`documented_only` na base), diga isso no passo correspondente.

## Evidências dos passos
- `path`: exatamente como aparece depois de "===" ou nas evidências da base.
- `line_start` e `line_end`: as linhas que mostram o passo (no máximo 30).
- `quote`: trecho CURTO (até 120 caracteres) copiado literalmente de dentro dessas linhas, sem o número da linha.
- `source_type`: "code" ou "idea_doc".

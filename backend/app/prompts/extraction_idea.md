# Tarefa: promessas do documento da ideia

Você recebe documentos sobre um produto (documento da ideia, escopo, transcrição de reunião ou texto livre). Liste as funcionalidades que esses documentos PROMETEM que o produto terá.

## O que é uma promessa
- Uma funcionalidade que a pessoa usuária ou o negócio percebe. Exemplos: "Cupom de desconto no checkout", "Login com e-mail e senha".
- NÃO são promessas: requisitos genéricos ("ser rápido", "usar nuvem"), tarefas do projeto (prazos, reuniões, responsáveis) e detalhes de tecnologia.
- Junte menções repetidas da mesma funcionalidade em uma só promessa.
- Inclua também o que foi prometido para uma versão futura ou de forma vaga, desde que seja uma funcionalidade do produto.

## Campos
- `id`: P1, P2, P3... na ordem em que aparecem no material.
- `name`: curto (até 8 palavras).
- `description`: uma ou duas frases dizendo o que a funcionalidade faz, segundo o documento.
- No máximo 30 promessas. Se os documentos não prometerem nenhuma funcionalidade, devolva a lista vazia.

## Evidências (obrigatórias)
- Cada promessa tem 1 ou 2 evidências.
- `path`: o caminho exatamente como aparece depois de "===".
- `line_start` e `line_end`: as linhas onde a promessa aparece (intervalo de no máximo 15 linhas).
- `quote`: um trecho CURTO (até 120 caracteres) copiado literalmente de dentro dessas linhas, sem o número da linha. Não resuma, não traduza e não corrija o trecho.
- `source_type`: "idea_doc".

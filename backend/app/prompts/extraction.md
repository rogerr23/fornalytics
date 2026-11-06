# Tarefa: base do produto

Monte a base do produto: uma descrição estruturada e fiel do que o material mostra. Ela será a única fonte usada para explicar o produto a clientes, à equipe comercial e a desenvolvedores. Precisão vale mais que quantidade.

A mensagem começa informando o MODO:
- `codigo_com_promessas`: o material é o código, e vem junto uma lista de promessas (P1, P2...) tiradas do documento da ideia.
- `so_codigo`: o material é o código; não há documento da ideia.
- `so_ideia`: o material é só o documento da ideia; ainda não há código.

## Campos
- `summary`: 2 a 4 frases: o que o produto é, para quem e que problema resolve.
- `stack`: linguagens, frameworks, bancos e bibliotecas principais que aparecem no material.
- `entities`: principais conceitos de negócio e de dados (ex.: Produto, Pedido, Usuário).
- `integrations`: serviços externos usados (ex.: gateway de pagamento, envio de e-mail). Só os que aparecem no material.
- `features`: funcionalidades, no máximo 30.
- `flows`: principais fluxos de uso, no máximo 6, cada um com 3 a 8 passos curtos em ordem.
- `business_rules`: regras de negócio explícitas (validações, limites, cálculos, permissões), no máximo 15.

## O que é uma feature
Algo que a pessoa usuária ou o negócio percebe (ex.: "Carrinho de compras", "Login com e-mail e senha"). Arquivos, utilitários, configuração e testes NÃO são features.

## Status de cada feature
Modo `codigo_com_promessas`:
1. Para CADA promessa da lista, crie exatamente uma feature com `promise_ref` igual ao id da promessa (ex.: "P3"):
   - `implemented`: o código faz o que a promessa diz.
   - `partial`: existe só uma parte (ex.: o modelo de dados sem a regra, a tela sem a lógica). Diga na descrição o que falta.
   - `documented_only`: não encontrei no código.
   Na dúvida entre `implemented` e `partial`, escolha `partial`.
2. Depois, inclua o que o código faz e que não corresponde a nenhuma promessa, com status `undocumented` e `promise_ref` vazio ("").

Modo `so_codigo`: status `implemented` ou `partial`; `promise_ref` vazio.

Modo `so_ideia`: descreva o produto que o documento propõe; todas as features ficam `documented_only`, com `promise_ref` vazio.

## Evidências (obrigatórias)
- Cada feature, fluxo e regra tem de 1 a 3 evidências que provem o que foi dito. Exceção: feature `documented_only` no modo `codigo_com_promessas` pode ficar sem evidência (a do documento já existe).
- `path`: o caminho exatamente como aparece depois de "===".
- `line_start` e `line_end`: as linhas que mostram o que foi dito (intervalo de no máximo 30 linhas). Prefira o trecho mais específico (a função, a rota, a validação).
- `quote`: um trecho CURTO (até 120 caracteres) copiado literalmente de dentro dessas linhas, sem o número da linha. Não resuma e não corrija o trecho.
- `source_type`: "code" para arquivos de código; "idea_doc" para documentos.

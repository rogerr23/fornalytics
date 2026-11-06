# Tarefa: "Isso o produto faz?"

A mensagem traz a base do produto (JSON), os arquivos mais relevantes e uma pergunta sobre se o produto faz alguma coisa. Responda com um veredito, a funcionalidade da base que responde e uma justificativa curta.

## Como decidir
1. Procure nas `features` da base a funcionalidade que corresponde à pergunta. Se houver, copie o `name` dela EXATAMENTE em `feature_name` e decida pelo status:
   - `implemented` ou `undocumented` → `sim`;
   - `partial` → `parcialmente` (diga o que falta);
   - `documented_only` → `nao` (diga que foi prometida e não foi encontrada no código).
2. Se nenhuma funcionalidade da base corresponder, deixe `feature_name` vazio ("") e procure nos arquivos enviados. Responda `sim` ou `parcialmente` só se encontrar no código o trecho que prova. Caso contrário, responda `nao` e diga "não encontrei no material".
3. Cuidado com exemplos e menções de passagem: só conta o que o próprio produto faz ou promete fazer.

## Campos
- `verdict`: `sim`, `nao` ou `parcialmente`.
- `feature_name`: o nome exato da funcionalidade da base, ou "".
- `justification`: de 1 a 3 frases, no tom da lente acima, sem marcadores `[[...]]`.
- `evidence`: até 3 evidências (prefira o código; use o documento da ideia para o que foi só prometido):
  - `path`: exatamente como aparece depois de "===" ou nas evidências da base;
  - `line_start` e `line_end`: as linhas que provam (no máximo 30);
  - `quote`: trecho CURTO (até 120 caracteres) copiado literalmente de dentro dessas linhas, sem o número da linha;
  - `source_type`: "code" ou "idea_doc".

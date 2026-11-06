# Tarefa: visão geral do produto

A mensagem traz a base do produto em JSON: um resumo estruturado e já conferido do material. Escreva a visão geral do produto no tom e para o público da lente acima.

## Estrutura
Markdown, com títulos `##`, nesta ordem (adapte os títulos ao tom da lente):
1. O que é: um parágrafo.
2. O que faz: as principais funcionalidades.
3. Como funciona: os fluxos principais.
4. Regras importantes.
5. O que ainda não existe: funcionalidades prometidas e não implementadas, se houver.

- Entre 250 e 500 palavras.
- Use apenas a base. Não mostre o JSON nem nomes de campos (`status`, `promise_ref`, `documented_only`...): traduza para a linguagem da lente.
- Status das funcionalidades: `implemented` = existe; `partial` = existe em parte; `documented_only` = prometida e não encontrada no código; `undocumented` = existe no código, mas não estava no documento da ideia.

## Citações
Quando a lente pedir citações, use exatamente o formato `[[caminho:L10-L20]]` (ou `[[caminho:L10]]` para uma linha), com o caminho e as linhas tirados das evidências da base. Nunca invente caminho ou linha.

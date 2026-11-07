# 0004 — Identidade visual do Extreme Group Design System

- **Data:** 2026-11-06
- **Status:** aceita

## Contexto

O frontend usava o visual padrão do Tailwind (cinza e índigo), sem identidade. O Roger pediu um estilo diferente e melhorias de UX. Foram feitos quatro protótipos da mesma tela (Ideia × Código), num canvas de design:

- A, editorial;
- B, ferramenta de dev;
- C, amigável e colorido;
- D, seguindo o Extreme Group Design System, já publicado na organização.

## Opções consideradas

1. **A, editorial:** serifa e fundo creme. Elegante, mas foge do contexto corporativo do programa.
2. **B, ferramenta de dev:** escuro e monoespaçado. Agrada a lente técnica, mas afasta o público cliente e não técnico.
3. **C, colorido:** uma cor por lente. Amigável, mas cria uma identidade nova sem relação com a empresa.
4. **D, Extreme Group:** monocromático, Montserrat e cantos retos. Combina com o programa de estágio da Extreme e já tem regras prontas (tipografia, espaçamento, status).

## Decisão

Opção D, escolhida pelo Roger. Ela é aplicada assim:

- **Tokens:** os valores do design system viram tokens no `@theme` do Tailwind v4 (`frontend/src/index.css`). As cores padrão são desligadas com `--color-*: initial`.
- **Fonte:** Montserrat embutida via `@fontsource-variable/montserrat`, para funcionar sem internet.
- **Ícones:** de traço, em SVG próprio (`shared/ui/Icon.tsx`), no lugar dos emojis, que o design system proíbe.
- **Componentes:** os do design system não são importados (o pacote dele é um bundle para canvas, não um pacote npm). Os componentes de `shared/ui` foram refeitos seguindo as mesmas regras.

## Consequências

- **Marca consistente:** uma classe de cor fora da marca (por exemplo `bg-indigo-600`) não gera estilo, o que impede cores soltas.
- **Contraste:** o cinza-aço `#90A0AD` só aparece em números grandes sobre preto. Sobre branco, os números usam `#6B767F`, porque o aço não atinge o contraste mínimo.
- **Cor de aviso:** o âmbar de status foi escurecido para `#8A5800`, porque o `#A86B00` do design system fica abaixo de 4,5:1 em texto pequeno.
- **Ícones da marca:** se a Extreme tiver um conjunto oficial de ícones, ele substitui o `Icon.tsx` sem mexer nas telas.
- **Mudança de identidade:** trocar de identidade no futuro é editar os tokens e o `shared/ui`; as features quase não têm cor própria.

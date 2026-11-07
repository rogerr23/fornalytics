# Identidade visual

O frontend segue o **Extreme Group Design System** (decisão em [ADR 0004](adr/0004-identidade-visual-extreme.md)). Os tokens ficam em `frontend/src/index.css` e os componentes base em `frontend/src/shared/ui/`.

## Princípios

- **Monocromático:** preto, branco e cinza. A cor aparece só em status (sucesso, aviso, erro, informação), sempre apagada.
- **Montserrat** em tudo. Títulos misturam pesos: leve + extranegrito ("Seus **projetos**", "Ideia **× Código**").
- **Cantos retos:** 4 px em controles, 8 px em cartões e pílula só em etiquetas (`Badge`).
- **Estrutura por linhas, não por sombras:** cartões com linha de 1 px. Sombra só no que flutua (painel de citação).
- **Sem degradê, sem emoji.** Ícones de traço de 1,5 px em `currentColor` (`Icon.tsx`).
- **Etiquetas pequenas** em maiúsculas com espaçamento largo (utilitário `eyebrow`).
- **Números grandes** em cinza com a legenda abaixo, primeira palavra em negrito (`Stat`).

## Tokens (`@theme`)

As cores padrão do Tailwind estão desligadas (`--color-*: initial`), então só estas classes existem:

| Token | Valor | Uso |
|---|---|---|
| `ink` | `#000000` | Texto, botão principal, faixa preta |
| `ink-800` / `ink-700` / `ink-600` | `#1A1A1A` / `#2E2E2E` / `#4A4A4A` | Texto longo, hover do preto, texto secundário forte |
| `grey-500` | `#6B767F` | Texto secundário, números grandes sobre branco (4,6:1) |
| `grey-400` | `#90A0AD` | Cinza-aço: números grandes **só sobre preto** |
| `grey-300` / `grey-200` | `#C9D1D7` / `#E8EBEE` | Linhas visíveis / linhas internas |
| `grey-100` / `grey-50` | `#F3F3F3` / `#FAFAFA` | Fundos sutis, hover |
| `success` / `warning` / `danger` / `info` | `#1F7A4D` / `#8A5800` / `#B3261E` / `#14145A` | Status (cada um com `-tint` para fundo) |

`warning` é mais escuro que o do design system (`#A86B00`) para passar de 4,5:1 em texto pequeno.

## Componentes (`shared/ui`)

| Componente | Para quê |
|---|---|
| `Button`, `ButtonLink`, `buttonClass` | Botões `primary` (preto), `secondary` (contorno), `ghost`, `ghostInverse` (sobre preto), `danger`, `inverse`. `ButtonLink` é um link de navegação com cara de botão (nunca botão dentro de link) |
| `Card`, `CardTitle` | Cartão com linha fina; título com contagem opcional |
| `Badge`, `ProjectStatusBadge` | Etiquetas de status em pílula |
| `Alert` | Aviso com ícone e ação opcional |
| `Tabs` | Abas sublinhadas; rolam de lado no celular, ou quebram a linha com `wrap` |
| `Page` | `PageBody` (largura e espaçamento), `PageHeader`, `Breadcrumbs`, `HeroBand` (faixa preta), `Stat` |
| `Steps` | Etapas da jornada: nome → material → processamento → explicações |
| `Dropzone` | Arrastar e soltar arquivo, com o campo de arquivo nativo por baixo |
| `Skeleton`, `SkeletonText`, `EmptyState`, `Spinner` | Carregamento e telas vazias |
| `Icon` | Ícones de traço; nomes em `PATHS` |
| `field.ts` | Classes de campos de texto (`FIELD`) e rótulos (`LABEL`) |

## Acessibilidade

- Contraste de 4,5:1 no texto; o cinza-aço só aparece em números grandes sobre preto.
- Foco visível: contorno preto de 2 px (branco sobre a faixa preta, com a classe `on-dark`).
- Alvos de toque de pelo menos 44 px nos controles principais.
- Link "Pular para o conteúdo" no topo.
- Animações desligadas para quem configurou "reduzir movimento" no sistema.
- Todas as telas funcionam na largura do celular, sem rolagem lateral.

## Ao criar uma tela nova

1. Monte com `PageBody`, `PageHeader` e os componentes acima. Evite classes de cor soltas nas features.
2. Precisou de um ícone? Acrescente o desenho em `Icon.tsx` (traço, 24×24).
3. Precisou de uma cor nova? Ela entra como token no `@theme`, com contraste conferido, e é registrada aqui.

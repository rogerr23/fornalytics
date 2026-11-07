# Roteiro da demo

Apresentação do Fornalytics com a **Loja Aurora** (`demo/`), um app pequeno e próprio com lacunas propositais no escopo. Tempo total: cerca de **10 minutos**.

## Antes da apresentação (no dia anterior ou de manhã)

O plano gratuito da IA tem limite diário e oscila (503). **Nada que dependa da IA deve acontecer pela primeira vez ao vivo.**

1. `npm run dev` e abrir http://localhost:5173. O rodapé da lista de projetos deve mostrar API, banco e IA em verde.
2. `npm run demo:zip`.
3. Criar o projeto **Loja Aurora** e enviar `demo/loja.zip` como **Código (.zip)** e `demo/escopo.md` como **Documento → Documento da ideia / escopo**.
4. Clicar em **Processar** e esperar a base ficar pronta (2 chamadas).
5. **Aquecer o cache:** abrir a **Visão geral** nas três lentes (3 chamadas). Depois disso, a visão geral e o Ideia × Código abrem na hora, sem IA.
6. Fazer uma vez as perguntas da apresentação (abaixo) para conferir as respostas, já que chat, lado a lado, "Isso faz?" e fluxo chamam a IA a cada pergunta. Se algo sair diferente do esperado, ver o plano B.
7. Total: cerca de 10 chamadas, bem dentro do limite diário.

## Roteiro ao vivo

| # | Tempo | Quem | O que fazer | O que mostrar |
|---|---|---|---|---|
| 1 | 1 min | Ana (PO) | Abrir **Novo projeto** e mostrar o envio do zip e do escopo; mostrar o resumo da ingestão (arquivos lidos, ignorados, tokens) | O material é lido na hora, sem IA, e nada fica de fora sem aviso |
| 2 | 1 min | Ana | Abrir o projeto **já processado**; mostrar a **Visão geral** na lente **Não técnico** | A base pronta; citações conferidas |
| 3 | 1 min | Ana | Trocar para a lente **Cliente** | Mesmo produto, sem jargão |
| 4 | 1,5 min | Bruno (comercial) | **Isso faz?** → "O sistema gera nota fiscal?" | **Não.** Prometida no escopo, não encontrada no código, com a evidência do escopo |
| 5 | 1,5 min | Carla (dev nova) | Lente **Técnico** → **Chat** → "Como funciona o login?" | Resposta com links para `authService.ts` e `middleware/auth.ts`; clicar numa citação abre o trecho |
| 6 | 1,5 min | Ana | **Lado a lado** → "Como funciona o frete?" | As três lentes dizem a mesma regra (grátis a partir de R$ 199, senão R$ 19,90) em tons diferentes |
| 7 | 1 min | Ana | **Ideia × Código** | ✅ 6 entregues, ⚠️ cupom e nota fiscal, 🔍 lista de desejos: o risco aparece antes da entrega |
| 8 | 1 min | Carla | **Fluxos** → "O que acontece quando o cliente finaliza a compra?" | Passo a passo com o diagrama: confere estoque, cobra o cartão, recusado ou aprovado, baixa estoque, e-mail |

Passos extras, se sobrar tempo:
- **Isso faz?** → "Tem cupom de desconto?": **Não**;
- **Isso faz?** → "Dá para salvar produtos para comprar depois?": **Sim**, existe no código e não estava no escopo.

## Respostas esperadas

| Pergunta / tela | Esperado | Onde está no código ou no escopo |
|---|---|---|
| Ideia × Código ✅ | Catálogo (busca e categorias), cadastro e login, carrinho, checkout com cartão, e-mail de confirmação, histórico de pedidos | `src/routes/*`, `src/services/*` |
| Ideia × Código ⚠️ | Cupom de desconto; emissão de nota fiscal | `escopo.md`, itens 5 e 7 |
| Ideia × Código 🔍 | Lista de desejos | `src/routes/wishlist.ts`, `src/services/wishlistService.ts` |
| "O sistema gera nota fiscal?" | Não (prometida, não implementada) | `escopo.md`, item 7 |
| "Tem cupom de desconto?" | Não (prometida, não implementada) | `escopo.md`, item 5 |
| "Dá para salvar produtos para comprar depois?" | Sim (não documentada) | `src/services/wishlistService.ts` |
| "Como funciona o login?" (técnico) | E-mail e senha, senha com hash `scrypt` e sal, token com validade de 12 horas, rota protegida por `requireAuth` | `src/services/authService.ts`, `src/middleware/auth.ts`, `src/config.ts` |
| "Como funciona o frete?" | Grátis a partir de R$ 199; abaixo, R$ 19,90 | `src/config.ts`, `shippingFor` em `src/services/checkoutService.ts` |
| Fluxo do checkout | Carrinho vazio? → confere estoque → cobra o cartão → recusado (402) ou aprovado → baixa estoque → limpa carrinho → e-mail | `checkout` em `src/services/checkoutService.ts` |
| Regras de negócio | Estoque nunca negativo, até 10 unidades por produto, frete grátis a partir de R$ 199, senha com 8 caracteres | `cartService.ts`, `checkoutService.ts`, `authService.ts`, `config.ts` |

## Plano B (se a IA falhar ao vivo)

| Situação | O que fazer |
|---|---|
| 429 ou 503 numa pergunta | Mostrar o aviso amigável (faz parte da história: "a tela nunca quebra") e usar a resposta já feita no ensaio, que continua na aba enquanto ela estiver aberta, ou a reserva em `demo/reserva/` |
| Cota do dia acabou | Visão geral (cache), Ideia × Código e Fluxos da base funcionam sem IA. Para as outras abas, usar as respostas de reserva em `demo/reserva/` (geradas pelo `npm run eval`, uma por pergunta do roteiro) |
| Backend fora | `npm run dev` de novo; o projeto e a base estão no banco (Neon) |
| Neon "dormindo" | A primeira requisição pode levar alguns segundos; recarregar a página |

## Resultado da rodada real

Preencher depois da rodada de ponta a ponta com o Gemini (data, modelo, o que bateu e o que não bateu).

_Pendente: a cota diária do plano gratuito acabou em 06/11/2026._

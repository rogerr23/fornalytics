# Loja Aurora

Loja online de artigos para casa. API REST em TypeScript com Express.

## Como rodar

```bash
npm install
npm run dev
```

A API sobe em `http://localhost:3000`. Os dados ficam em memória e voltam ao estado inicial a cada reinício.

## Rotas

| Método | Rota | O que faz |
|---|---|---|
| POST | `/auth/register` | Cria uma conta |
| POST | `/auth/login` | Entra e recebe um token |
| GET | `/products` | Lista produtos (busca por `q` e filtro por `category`) |
| GET | `/products/:id` | Detalhe de um produto |
| GET | `/cart` | Carrinho do cliente |
| POST | `/cart/items` | Adiciona um produto ao carrinho |
| PATCH | `/cart/items/:productId` | Muda a quantidade |
| DELETE | `/cart/items/:productId` | Remove do carrinho |
| POST | `/checkout` | Fecha o pedido e cobra no cartão |
| GET | `/orders` | Histórico de pedidos do cliente |
| GET | `/orders/:id` | Detalhe de um pedido |
| GET | `/wishlist` | Produtos salvos para depois |
| POST | `/wishlist/:productId` | Salva um produto |
| DELETE | `/wishlist/:productId` | Remove um produto salvo |

As rotas de carrinho, checkout, pedidos e lista de desejos exigem o cabeçalho `Authorization: Bearer <token>`.

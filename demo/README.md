# Demo do Fornalytics

Material controlado para a apresentação: um app pequeno e próprio e um documento de escopo com **lacunas propositais**. Assim o resultado de cada aba é previsível. O roteiro completo da apresentação está em [`docs/demo-script.md`](../docs/demo-script.md).

| Arquivo | O que é |
|---|---|
| `loja/` | **Loja Aurora**: API de uma loja online em TypeScript + Express (catálogo, login, carrinho, checkout com pagamento simulado, e-mail de confirmação, pedidos e lista de desejos). É material de entrada: não é instalada nem rodada pelo Fornalytics |
| `escopo.md` | Escopo do MVP da loja (o "documento da ideia") |
| `loja.zip` | Gerado por `npm run demo:zip` (fora do Git) |

## Lacunas propositais

| Funcionalidade | No escopo | No código | Coluna esperada no Ideia × Código |
|---|---|---|---|
| Catálogo com busca e categorias | ✔ | ✔ | ✅ Prometido e implementado |
| Cadastro e login | ✔ | ✔ | ✅ |
| Carrinho | ✔ | ✔ | ✅ |
| Checkout com cartão (e frete) | ✔ | ✔ | ✅ |
| E-mail de confirmação | ✔ | ✔ | ✅ |
| Histórico de pedidos | ✔ | ✔ | ✅ |
| **Cupom de desconto** | ✔ | ✘ | ⚠️ Prometido e não implementado |
| **Emissão de nota fiscal** | ✔ | ✘ | ⚠️ Prometido e não implementado |
| **Lista de desejos** | ✘ | ✔ | 🔍 Implementado e não documentado |

As quatro regras de negócio do escopo (estoque, 10 unidades por produto, frete grátis a partir de R$ 199 e senha com 8 caracteres) estão no código: `src/config.ts`, `src/services/cartService.ts`, `src/services/checkoutService.ts` e `src/services/authService.ts`.

**Cuidado ao mexer:** o `loja/README.md` é lido primeiro pela ingestão. Ele não pode citar cupom nem nota fiscal; senão as lacunas deixam de ser lacunas.

## Como usar

```bash
npm run demo:zip
```

No Fornalytics: crie um projeto, envie `demo/loja.zip` como **Código** e `demo/escopo.md` como **Documento da ideia** e clique em **Processar**.

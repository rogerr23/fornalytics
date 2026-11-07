import type { Order } from '../models/order.js'
import type { User } from '../models/user.js'

const brl = (value: number) =>
  value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })

/** Order confirmation e-mail. Printed to the console instead of a real mail provider. */
export async function sendOrderConfirmation(user: User, order: Order): Promise<void> {
  const lines = order.items.map((item) => `- ${item.quantity}x ${item.name}: ${brl(item.unitPrice * item.quantity)}`)
  const body = [
    `Olá, ${user.name}!`,
    `Recebemos o pagamento do pedido ${order.id}.`,
    ...lines,
    `Frete: ${order.shipping === 0 ? 'grátis' : brl(order.shipping)}`,
    `Total: ${brl(order.total)}`,
  ].join('\n')
  console.log(`[e-mail para ${user.email}] Pedido confirmado\n${body}`)
}

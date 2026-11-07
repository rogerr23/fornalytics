import { randomUUID } from 'node:crypto'
import { config } from '../config.js'
import { db } from '../db.js'
import { badRequest, HttpError } from '../errors.js'
import type { Order, OrderItem } from '../models/order.js'
import type { User } from '../models/user.js'
import { clearCart, getCart } from './cartService.js'
import { getProduct } from './catalogService.js'
import { sendOrderConfirmation } from './emailService.js'
import { chargeCard, type CardData } from './paymentGateway.js'

const round = (value: number) => Math.round(value * 100) / 100

/** Free shipping at or above the threshold; flat fee below it. */
export function shippingFor(subtotal: number): number {
  return subtotal >= config.freeShippingThreshold ? 0 : config.shippingFee
}

export interface Totals {
  items: OrderItem[]
  subtotal: number
  shipping: number
  total: number
}

export function cartTotals(userId: string): Totals {
  const items = getCart(userId).items.map((item) => {
    const product = getProduct(item.productId)
    return { productId: product.id, name: product.name, unitPrice: product.price, quantity: item.quantity }
  })
  const subtotal = round(items.reduce((sum, item) => sum + item.unitPrice * item.quantity, 0))
  const shipping = items.length ? shippingFor(subtotal) : 0
  return { items, subtotal, shipping, total: round(subtotal + shipping) }
}

/**
 * Closes the order: checks stock again, charges the card, lowers the stock,
 * saves the order, empties the cart and sends the confirmation e-mail.
 */
export async function checkout(user: User, card: CardData): Promise<Order> {
  const totals = cartTotals(user.id)
  if (totals.items.length === 0) throw badRequest('O carrinho está vazio.')

  // Stock may have changed since the item went into the cart.
  for (const item of totals.items) {
    const product = getProduct(item.productId)
    if (item.quantity > product.stock) {
      throw new HttpError(409, `"${product.name}" não tem mais estoque suficiente.`)
    }
  }

  const payment = await chargeCard(card, totals.total)
  const order: Order = {
    id: randomUUID(),
    userId: user.id,
    ...totals,
    status: payment.approved ? 'paid' : 'payment_failed',
    paymentId: payment.paymentId,
    createdAt: new Date(),
  }
  db.orders.set(order.id, order)

  if (!payment.approved) {
    throw new HttpError(402, payment.reason ?? 'Pagamento não aprovado.')
  }

  for (const item of totals.items) {
    const product = getProduct(item.productId)
    product.stock -= item.quantity // never negative: checked above
  }
  clearCart(user.id)
  await sendOrderConfirmation(user, order)
  return order
}

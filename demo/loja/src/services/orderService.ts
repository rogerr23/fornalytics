import { db } from '../db.js'
import { notFound } from '../errors.js'
import type { Order } from '../models/order.js'

/** Customer's orders, newest first. */
export function listOrders(userId: string): Order[] {
  return [...db.orders.values()]
    .filter((order) => order.userId === userId)
    .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
}

export function getOrder(userId: string, orderId: string): Order {
  const order = db.orders.get(orderId)
  if (!order || order.userId !== userId) throw notFound('Pedido')
  return order
}

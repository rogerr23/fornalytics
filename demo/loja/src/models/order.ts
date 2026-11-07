export type OrderStatus = 'paid' | 'payment_failed'

export interface OrderItem {
  productId: string
  name: string
  unitPrice: number
  quantity: number
}

export interface Order {
  id: string
  userId: string
  items: OrderItem[]
  subtotal: number
  shipping: number
  total: number
  status: OrderStatus
  paymentId: string | null
  createdAt: Date
}

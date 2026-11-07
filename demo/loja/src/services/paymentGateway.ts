import { randomUUID } from 'node:crypto'

export interface CardData {
  number: string
  holder: string
  expiry: string // MM/AA
  cvv: string
}

export interface PaymentResult {
  approved: boolean
  paymentId: string | null
  reason?: string
}

/**
 * Simulated card gateway (stand-in for the real provider).
 * Cards ending in 0000 are declined, to test the failure path.
 */
export async function chargeCard(card: CardData, amount: number): Promise<PaymentResult> {
  const digits = card.number.replace(/\D/g, '')
  if (digits.length < 13 || digits.length > 19) {
    return { approved: false, paymentId: null, reason: 'Número de cartão inválido.' }
  }
  if (!/^\d{2}\/\d{2}$/.test(card.expiry) || !/^\d{3,4}$/.test(card.cvv)) {
    return { approved: false, paymentId: null, reason: 'Dados do cartão incompletos.' }
  }
  if (digits.endsWith('0000')) {
    return { approved: false, paymentId: null, reason: 'Pagamento recusado pela operadora.' }
  }
  if (amount <= 0) return { approved: false, paymentId: null, reason: 'Valor inválido.' }
  return { approved: true, paymentId: `pay_${randomUUID()}` }
}

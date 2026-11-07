/** Business settings of the store. Values in BRL. */
export const config = {
  port: Number(process.env.PORT ?? 3000),
  /** Orders at or above this subtotal ship for free. */
  freeShippingThreshold: 199,
  shippingFee: 19.9,
  /** Maximum units of the same product in one cart. */
  maxQuantityPerItem: 10,
  minPasswordLength: 8,
  /** How long a login token stays valid. */
  sessionHours: 12,
}

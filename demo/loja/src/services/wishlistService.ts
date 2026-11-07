import { db } from '../db.js'
import type { Product } from '../models/product.js'
import { getProduct } from './catalogService.js'

/** Products the customer saved to buy later. */
export function listWishlist(userId: string): Product[] {
  const ids = db.wishlists.get(userId) ?? new Set<string>()
  return [...ids].map((id) => getProduct(id))
}

export function addToWishlist(userId: string, productId: string): Product[] {
  getProduct(productId) // 404 for unknown products
  const ids = db.wishlists.get(userId) ?? new Set<string>()
  ids.add(productId)
  db.wishlists.set(userId, ids)
  return listWishlist(userId)
}

export function removeFromWishlist(userId: string, productId: string): Product[] {
  db.wishlists.get(userId)?.delete(productId)
  return listWishlist(userId)
}

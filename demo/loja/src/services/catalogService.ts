import { db } from '../db.js'
import { notFound } from '../errors.js'
import type { Category, Product } from '../models/product.js'

export interface CatalogFilter {
  q?: string
  category?: Category
}

function normalize(text: string): string {
  return text.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
}

/** Search by name or description (accents ignored) and filter by category. */
export function listProducts(filter: CatalogFilter = {}): Product[] {
  const query = filter.q ? normalize(filter.q) : ''
  return [...db.products.values()].filter((product) => {
    if (filter.category && product.category !== filter.category) return false
    if (!query) return true
    return normalize(`${product.name} ${product.description}`).includes(query)
  })
}

export function getProduct(id: string): Product {
  const product = db.products.get(id)
  if (!product) throw notFound('Produto')
  return product
}

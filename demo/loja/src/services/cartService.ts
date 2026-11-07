import { config } from '../config.js'
import { db } from '../db.js'
import { badRequest } from '../errors.js'
import type { Cart } from '../models/cart.js'
import { getProduct } from './catalogService.js'

export function getCart(userId: string): Cart {
  let cart = db.carts.get(userId)
  if (!cart) {
    cart = { userId, items: [] }
    db.carts.set(userId, cart)
  }
  return cart
}

/** Quantity rules: at least 1, at most maxQuantityPerItem, never above the stock. */
function checkQuantity(productId: string, quantity: number): void {
  if (!Number.isInteger(quantity) || quantity < 1) throw badRequest('Quantidade inválida.')
  if (quantity > config.maxQuantityPerItem) {
    throw badRequest(`Limite de ${config.maxQuantityPerItem} unidades por produto.`)
  }
  const product = getProduct(productId)
  if (quantity > product.stock) {
    throw badRequest(`Só temos ${product.stock} unidade(s) de "${product.name}" em estoque.`)
  }
}

export function addItem(userId: string, productId: string, quantity = 1): Cart {
  const cart = getCart(userId)
  const item = cart.items.find((i) => i.productId === productId)
  const newQuantity = (item?.quantity ?? 0) + quantity
  checkQuantity(productId, newQuantity)
  if (item) item.quantity = newQuantity
  else cart.items.push({ productId, quantity })
  return cart
}

export function setQuantity(userId: string, productId: string, quantity: number): Cart {
  const cart = getCart(userId)
  const item = cart.items.find((i) => i.productId === productId)
  if (!item) throw badRequest('Este produto não está no carrinho.')
  checkQuantity(productId, quantity)
  item.quantity = quantity
  return cart
}

export function removeItem(userId: string, productId: string): Cart {
  const cart = getCart(userId)
  cart.items = cart.items.filter((i) => i.productId !== productId)
  return cart
}

export function clearCart(userId: string): void {
  db.carts.delete(userId)
}

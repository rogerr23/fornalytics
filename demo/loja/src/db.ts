import type { Cart } from './models/cart.js'
import type { Order } from './models/order.js'
import type { Product } from './models/product.js'
import type { Session, User } from './models/user.js'

/** In-memory storage. Restarting the server brings back the sample catalog. */
export const db = {
  products: new Map<string, Product>(),
  users: new Map<string, User>(),
  sessions: new Map<string, Session>(),
  carts: new Map<string, Cart>(),
  orders: new Map<string, Order>(),
  /** Saved products per customer (userId -> productIds). */
  wishlists: new Map<string, Set<string>>(),
}

const SAMPLE_PRODUCTS: Product[] = [
  { id: 'p1', name: 'Jogo de panelas inox', description: '5 peças, fundo triplo.', category: 'cozinha', price: 389.9, stock: 12 },
  { id: 'p2', name: 'Caneca de cerâmica', description: 'Feita à mão, 300 ml.', category: 'cozinha', price: 49.9, stock: 40 },
  { id: 'p3', name: 'Vaso de vidro', description: 'Vidro reciclado, 30 cm.', category: 'decoracao', price: 89.9, stock: 8 },
  { id: 'p4', name: 'Quadro abstrato', description: 'Impressão em canvas, 60 x 40 cm.', category: 'decoracao', price: 159.0, stock: 5 },
  { id: 'p5', name: 'Toalha de banho', description: 'Algodão egípcio.', category: 'banho', price: 79.9, stock: 30 },
  { id: 'p6', name: 'Jogo de lençol casal', description: '200 fios, 4 peças.', category: 'quarto', price: 219.0, stock: 15 },
]

for (const product of SAMPLE_PRODUCTS) db.products.set(product.id, product)

import { Router } from 'express'
import { currentUser, requireAuth, type AuthedRequest } from '../middleware/auth.js'
import { addItem, removeItem, setQuantity } from '../services/cartService.js'
import { cartTotals } from '../services/checkoutService.js'

export const cartRouter = Router()
cartRouter.use(requireAuth)

cartRouter.get('/', (req: AuthedRequest, res) => {
  res.json(cartTotals(currentUser(req).id))
})

cartRouter.post('/items', (req: AuthedRequest, res) => {
  const { productId, quantity = 1 } = req.body ?? {}
  addItem(currentUser(req).id, String(productId), Number(quantity))
  res.status(201).json(cartTotals(currentUser(req).id))
})

cartRouter.patch('/items/:productId', (req: AuthedRequest, res) => {
  setQuantity(currentUser(req).id, req.params.productId, Number(req.body?.quantity))
  res.json(cartTotals(currentUser(req).id))
})

cartRouter.delete('/items/:productId', (req: AuthedRequest, res) => {
  removeItem(currentUser(req).id, req.params.productId)
  res.json(cartTotals(currentUser(req).id))
})

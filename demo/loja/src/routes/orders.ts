import { Router } from 'express'
import { currentUser, requireAuth, type AuthedRequest } from '../middleware/auth.js'
import { getOrder, listOrders } from '../services/orderService.js'

export const ordersRouter = Router()
ordersRouter.use(requireAuth)

ordersRouter.get('/', (req: AuthedRequest, res) => {
  res.json(listOrders(currentUser(req).id))
})

ordersRouter.get('/:id', (req: AuthedRequest, res) => {
  res.json(getOrder(currentUser(req).id, req.params.id))
})

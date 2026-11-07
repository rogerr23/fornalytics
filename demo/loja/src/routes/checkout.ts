import { Router } from 'express'
import { currentUser, requireAuth, type AuthedRequest } from '../middleware/auth.js'
import { checkout } from '../services/checkoutService.js'

export const checkoutRouter = Router()
checkoutRouter.use(requireAuth)

/** Body: { card: { number, holder, expiry, cvv } } */
checkoutRouter.post('/', async (req: AuthedRequest, res, next) => {
  try {
    const order = await checkout(currentUser(req), req.body?.card ?? {})
    res.status(201).json(order)
  } catch (error) {
    next(error)
  }
})

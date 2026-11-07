import { Router } from 'express'
import { currentUser, requireAuth, type AuthedRequest } from '../middleware/auth.js'
import { addToWishlist, listWishlist, removeFromWishlist } from '../services/wishlistService.js'

export const wishlistRouter = Router()
wishlistRouter.use(requireAuth)

wishlistRouter.get('/', (req: AuthedRequest, res) => {
  res.json(listWishlist(currentUser(req).id))
})

wishlistRouter.post('/:productId', (req: AuthedRequest, res) => {
  res.status(201).json(addToWishlist(currentUser(req).id, req.params.productId))
})

wishlistRouter.delete('/:productId', (req: AuthedRequest, res) => {
  res.json(removeFromWishlist(currentUser(req).id, req.params.productId))
})

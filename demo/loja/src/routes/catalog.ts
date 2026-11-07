import { Router } from 'express'
import type { Category } from '../models/product.js'
import { getProduct, listProducts } from '../services/catalogService.js'

export const catalogRouter = Router()

catalogRouter.get('/', (req, res) => {
  const q = typeof req.query.q === 'string' ? req.query.q : undefined
  const category = typeof req.query.category === 'string' ? (req.query.category as Category) : undefined
  res.json(listProducts({ q, category }))
})

catalogRouter.get('/:id', (req, res) => {
  res.json(getProduct(req.params.id))
})

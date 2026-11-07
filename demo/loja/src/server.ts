import express, { type NextFunction, type Request, type Response } from 'express'
import { config } from './config.js'
import { HttpError } from './errors.js'
import { authRouter } from './routes/auth.js'
import { cartRouter } from './routes/cart.js'
import { catalogRouter } from './routes/catalog.js'
import { checkoutRouter } from './routes/checkout.js'
import { ordersRouter } from './routes/orders.js'
import { wishlistRouter } from './routes/wishlist.js'

const app = express()
app.use(express.json())

app.use('/auth', authRouter)
app.use('/products', catalogRouter)
app.use('/cart', cartRouter)
app.use('/checkout', checkoutRouter)
app.use('/orders', ordersRouter)
app.use('/wishlist', wishlistRouter)

// Expected errors keep their status and message; anything else is a 500.
app.use((error: unknown, _req: Request, res: Response, _next: NextFunction) => {
  if (error instanceof HttpError) {
    res.status(error.status).json({ error: error.message })
    return
  }
  console.error(error)
  res.status(500).json({ error: 'Erro inesperado. Tente de novo.' })
})

app.listen(config.port, () => {
  console.log(`Loja Aurora rodando em http://localhost:${config.port}`)
})

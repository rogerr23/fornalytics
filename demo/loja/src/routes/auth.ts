import { Router } from 'express'
import { login, register } from '../services/authService.js'

export const authRouter = Router()

authRouter.post('/register', (req, res) => {
  const { name = '', email = '', password = '' } = req.body ?? {}
  const user = register(name, email, password)
  res.status(201).json({ id: user.id, name: user.name, email: user.email })
})

authRouter.post('/login', (req, res) => {
  const { email = '', password = '' } = req.body ?? {}
  const session = login(email, password)
  res.json({ token: session.token, expiresAt: session.expiresAt })
})

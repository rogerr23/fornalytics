import type { NextFunction, Request, Response } from 'express'
import { unauthorized } from '../errors.js'
import type { User } from '../models/user.js'
import { userForToken } from '../services/authService.js'

export interface AuthedRequest extends Request {
  user?: User
}

/** Requires "Authorization: Bearer <token>" from a valid login. */
export function requireAuth(req: AuthedRequest, _res: Response, next: NextFunction): void {
  const token = req.header('authorization')?.replace(/^Bearer\s+/i, '')
  const user = token ? userForToken(token) : undefined
  if (!user) return next(unauthorized())
  req.user = user
  next()
}

export function currentUser(req: AuthedRequest): User {
  if (!req.user) throw unauthorized()
  return req.user
}

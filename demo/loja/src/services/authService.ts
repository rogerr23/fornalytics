import { randomBytes, randomUUID, scryptSync, timingSafeEqual } from 'node:crypto'
import { config } from '../config.js'
import { db } from '../db.js'
import { badRequest, HttpError } from '../errors.js'
import type { Session, User } from '../models/user.js'

const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function hashPassword(password: string, salt: string): string {
  return scryptSync(password, salt, 64).toString('hex')
}

export function register(name: string, email: string, password: string): User {
  const normalized = email.trim().toLowerCase()
  if (!name.trim()) throw badRequest('Informe o nome.')
  if (!EMAIL.test(normalized)) throw badRequest('E-mail inválido.')
  if (password.length < config.minPasswordLength) {
    throw badRequest(`A senha precisa ter pelo menos ${config.minPasswordLength} caracteres.`)
  }
  const exists = [...db.users.values()].some((user) => user.email === normalized)
  if (exists) throw new HttpError(409, 'Já existe uma conta com este e-mail.')

  const salt = randomBytes(16).toString('hex')
  const user: User = {
    id: randomUUID(),
    name: name.trim(),
    email: normalized,
    passwordHash: hashPassword(password, salt),
    salt,
    createdAt: new Date(),
  }
  db.users.set(user.id, user)
  return user
}

export function login(email: string, password: string): Session {
  const user = [...db.users.values()].find((u) => u.email === email.trim().toLowerCase())
  const valid =
    user !== undefined &&
    timingSafeEqual(Buffer.from(hashPassword(password, user.salt), 'hex'), Buffer.from(user.passwordHash, 'hex'))
  if (!user || !valid) throw new HttpError(401, 'E-mail ou senha incorretos.')

  const session: Session = {
    token: randomBytes(24).toString('hex'),
    userId: user.id,
    expiresAt: new Date(Date.now() + config.sessionHours * 60 * 60 * 1000),
  }
  db.sessions.set(session.token, session)
  return session
}

/** The user behind a token, or undefined when the token is unknown or expired. */
export function userForToken(token: string): User | undefined {
  const session = db.sessions.get(token)
  if (!session) return undefined
  if (session.expiresAt.getTime() < Date.now()) {
    db.sessions.delete(token)
    return undefined
  }
  return db.users.get(session.userId)
}

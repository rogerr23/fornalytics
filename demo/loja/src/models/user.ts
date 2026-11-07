export interface User {
  id: string
  name: string
  email: string
  passwordHash: string
  salt: string
  createdAt: Date
}

export interface Session {
  token: string
  userId: string
  expiresAt: Date
}

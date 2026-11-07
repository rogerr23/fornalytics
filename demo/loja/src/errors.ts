/** An expected error with the HTTP status and the message shown to the customer. */
export class HttpError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message)
  }
}

export const notFound = (what: string) => new HttpError(404, `${what} não encontrado.`)
export const badRequest = (message: string) => new HttpError(400, message)
export const unauthorized = () => new HttpError(401, 'Faça login para continuar.')

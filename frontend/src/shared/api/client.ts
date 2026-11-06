/** Single HTTP client for the backend API. Every feature calls the API through here. */

const API_PREFIX = '/api'

const QUOTA_MESSAGE = 'O limite gratuito da IA foi atingido. Tente de novo em alguns instantes.'
const NETWORK_MESSAGE = 'Não foi possível falar com o servidor. Confira se o backend está rodando.'

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }

  /** Free-tier quota (429): shown as a friendly warning, never as a broken screen. */
  get isQuota(): boolean {
    return this.status === 429
  }
}

/** Raw request: throws ApiError on HTTP errors and network failures. */
export async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  let response: Response
  try {
    response = await fetch(`${API_PREFIX}${path}`, init)
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') throw error
    throw new ApiError(0, NETWORK_MESSAGE)
  }
  if (!response.ok) {
    throw new ApiError(response.status, await readErrorMessage(response))
  }
  return response
}

export async function apiGet<T>(path: string, signal?: AbortSignal): Promise<T> {
  return (await (await apiFetch(path, { signal })).json()) as T
}

export async function apiPost<T>(path: string, body?: unknown): Promise<T> {
  const response = await apiFetch(path, {
    method: 'POST',
    headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  return (await response.json()) as T
}

export async function apiPostForm<T>(path: string, form: FormData): Promise<T> {
  return (await (await apiFetch(path, { method: 'POST', body: form })).json()) as T
}

export async function apiDelete(path: string): Promise<void> {
  await apiFetch(path, { method: 'DELETE' })
}

/** Friendly text for any error a hook may surface. */
export function errorMessage(error: unknown): string {
  if (error instanceof ApiError)
    return error.isQuota && !error.message ? QUOTA_MESSAGE : error.message
  return 'Algo deu errado. Tente de novo.'
}

async function readErrorMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown }
    if (typeof body.detail === 'string') return body.detail
    // FastAPI validation errors (422) come as a list.
    if (Array.isArray(body.detail)) return 'Dados inválidos. Confira os campos e tente de novo.'
  } catch {
    // Not JSON: fall through.
  }
  return response.status === 429 ? QUOTA_MESSAGE : response.statusText || 'Erro no servidor.'
}

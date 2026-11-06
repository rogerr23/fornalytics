import { useQuery } from '@tanstack/react-query'
import { apiGet } from './client'

export type DatabaseStatus = 'ok' | 'unavailable' | 'not_configured'

export interface HealthResponse {
  status: 'ok'
  version: string
  database: DatabaseStatus
}

export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => apiGet<HealthResponse>('/health'),
  })
}

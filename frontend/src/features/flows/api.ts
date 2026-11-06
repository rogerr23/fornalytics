import { apiGet, apiPost } from '../../shared/api/client'
import type { Lens } from '../../shared/api/lens'
import type { Flow } from './types'

export function getBaseFlows(projectId: string, signal?: AbortSignal): Promise<Flow[]> {
  return apiGet<Flow[]>(`/projects/${projectId}/flows`, signal)
}

export function askFlow(projectId: string, question: string, lens: Lens): Promise<Flow> {
  return apiPost<Flow>(`/projects/${projectId}/flow`, { question, lens })
}

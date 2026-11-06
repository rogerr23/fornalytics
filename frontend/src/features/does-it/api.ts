import { apiPost } from '../../shared/api/client'
import type { Lens } from '../../shared/api/lens'
import type { DoesItResult } from './types'

export function askDoesIt(projectId: string, question: string, lens: Lens): Promise<DoesItResult> {
  return apiPost<DoesItResult>(`/projects/${projectId}/does-it`, { question, lens })
}

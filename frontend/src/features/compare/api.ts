import { apiPost } from '../../shared/api/client'
import type { CompareResult } from './types'

export function compareLenses(projectId: string, question: string): Promise<CompareResult> {
  return apiPost<CompareResult>(`/projects/${projectId}/compare-lenses`, { question })
}

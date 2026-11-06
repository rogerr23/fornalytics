import { apiGet } from '../../shared/api/client'
import type { IdeaVsCode } from './types'

export function getIdeaVsCode(projectId: string, signal?: AbortSignal): Promise<IdeaVsCode> {
  return apiGet<IdeaVsCode>(`/projects/${projectId}/idea-vs-code`, signal)
}

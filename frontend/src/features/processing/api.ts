import { apiFetch, apiPost } from '../../shared/api/client'
import { readSse } from '../../shared/api/sse'
import type { ProcessingStatus } from './types'

export function startProcessing(projectId: string): Promise<ProcessingStatus> {
  return apiPost<ProcessingStatus>(`/projects/${projectId}/process`)
}

/** SSE `status` events until the project stops processing (docs/api-events.md). */
export async function* streamStatus(
  projectId: string,
  signal: AbortSignal,
): AsyncGenerator<ProcessingStatus> {
  const response = await apiFetch(`/projects/${projectId}/status`, { signal })
  for await (const event of readSse(response)) {
    if (event.event === 'status') yield JSON.parse(event.data) as ProcessingStatus
  }
}

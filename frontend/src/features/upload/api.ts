import { apiDelete, apiPostForm } from '../../shared/api/client'
import type { IngestionSummary, NewSource } from './types'

export function addSource(projectId: string, source: NewSource): Promise<IngestionSummary> {
  const form = new FormData()
  if (source.kind === 'github') {
    form.append('type', 'code')
    form.append('url', source.url.trim())
    return apiPostForm<IngestionSummary>(`/projects/${projectId}/sources`, form)
  }
  form.append('type', source.type)
  if (source.kind === 'file') {
    form.append('file', source.file)
  } else {
    if (source.title.trim()) form.append('title', source.title.trim())
    form.append('content', source.content)
  }
  return apiPostForm<IngestionSummary>(`/projects/${projectId}/sources`, form)
}

export function deleteSource(projectId: string, sourceId: string): Promise<void> {
  return apiDelete(`/projects/${projectId}/sources/${sourceId}`)
}

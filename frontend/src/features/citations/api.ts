import { apiGet } from '../../shared/api/client'
import type { SourceType } from '../../shared/api/projects'

export interface FileContent {
  path: string
  source_type: SourceType
  line_count: number
  content: string
}

export function getFile(
  projectId: string,
  path: string,
  signal?: AbortSignal,
): Promise<FileContent> {
  return apiGet<FileContent>(
    `/projects/${projectId}/files?path=${encodeURIComponent(path)}`,
    signal,
  )
}

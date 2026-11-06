/** Project types and the query shared by several features (upload, processing, project page). */

import { queryOptions } from '@tanstack/react-query'
import { apiGet } from './client'

export type ProjectStatus = 'draft' | 'processing' | 'ready' | 'failed'
export type SourceType = 'code' | 'idea_doc' | 'transcript' | 'text'

export interface Project {
  id: string
  name: string
  status: ProjectStatus
  status_detail: string | null
  base_outdated: boolean
  created_at: string
}

export interface Source {
  id: string
  type: SourceType
  filename: string | null
  file_count: number
  token_estimate: number
  created_at: string
}

export interface FileRef {
  path: string
  token_estimate: number
  source_type: SourceType
}

export interface GroupLimit {
  total_tokens: number
  included_tokens: number
  excluded: FileRef[]
}

export interface Limits {
  budget_per_step: number
  documents: GroupLimit
  code: GroupLimit
}

export interface ProjectDetail extends Project {
  sources: Source[]
  limits: Limits
}

export const projectKeys = {
  all: ['projects'] as const,
  detail: (id: string) => ['projects', id] as const,
}

export function projectQuery(id: string) {
  return queryOptions({
    queryKey: projectKeys.detail(id),
    queryFn: ({ signal }) => apiGet<ProjectDetail>(`/projects/${id}`, signal),
  })
}

export const SOURCE_TYPE_LABEL: Record<SourceType, string> = {
  code: 'Código',
  idea_doc: 'Documento da ideia',
  transcript: 'Transcrição',
  text: 'Texto',
}

import { apiGet, apiPost } from '../../shared/api/client'
import type { Project } from '../../shared/api/projects'

export function listProjects(signal?: AbortSignal): Promise<Project[]> {
  return apiGet<Project[]>('/projects', signal)
}

export function createProject(name: string): Promise<Project> {
  return apiPost<Project>('/projects', { name })
}

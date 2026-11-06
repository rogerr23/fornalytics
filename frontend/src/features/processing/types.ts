import type { ProjectStatus } from '../../shared/api/projects'

export interface ProcessingStatus {
  status: ProjectStatus
  status_detail: string | null
  base_outdated: boolean
}

/** Every status seen on this screen, in order (the last one is the current). */
export interface ProcessingProgress {
  current: ProcessingStatus | null
  steps: string[]
}

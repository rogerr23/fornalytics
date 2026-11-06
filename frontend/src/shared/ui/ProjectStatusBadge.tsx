import type { ProjectStatus } from '../api/projects'
import { Badge } from './Badge'

const STATUS: Record<ProjectStatus, { label: string; tone: 'gray' | 'blue' | 'green' | 'red' }> = {
  draft: { label: 'Rascunho', tone: 'gray' },
  processing: { label: 'Processando', tone: 'blue' },
  ready: { label: 'Pronto', tone: 'green' },
  failed: { label: 'Falhou', tone: 'red' },
}

export function ProjectStatusBadge({ status }: { status: ProjectStatus }) {
  const view = STATUS[status]
  return <Badge tone={view.tone}>{view.label}</Badge>
}

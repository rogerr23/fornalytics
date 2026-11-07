import type { ProjectStatus } from '../api/projects'
import { Badge } from './Badge'

const STATUS: Record<
  ProjectStatus,
  { label: string; tone: 'neutral' | 'info' | 'success' | 'danger' }
> = {
  draft: { label: 'Rascunho', tone: 'neutral' },
  processing: { label: 'Processando', tone: 'info' },
  ready: { label: 'Pronto', tone: 'success' },
  failed: { label: 'Falhou', tone: 'danger' },
}

export function ProjectStatusBadge({ status }: { status: ProjectStatus }) {
  const view = STATUS[status]
  return <Badge tone={view.tone}>{view.label}</Badge>
}

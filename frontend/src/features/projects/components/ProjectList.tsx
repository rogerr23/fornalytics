import { Link } from 'react-router-dom'
import { errorMessage } from '../../../shared/api/client'
import type { Project } from '../../../shared/api/projects'
import { formatDate } from '../../../shared/lib/format'
import { Alert } from '../../../shared/ui/Alert'
import { ButtonLink } from '../../../shared/ui/Button'
import { EmptyState } from '../../../shared/ui/EmptyState'
import { Icon } from '../../../shared/ui/Icon'
import { ProjectStatusBadge } from '../../../shared/ui/ProjectStatusBadge'
import { Skeleton } from '../../../shared/ui/Skeleton'
import { useProjects } from '../hooks/useProjects'

/** Where each project opens: its current step in the journey. */
function projectLink(project: Project): string {
  switch (project.status) {
    case 'draft':
      return `/projects/${project.id}/material`
    case 'processing':
    case 'failed':
      return `/projects/${project.id}/processing`
    case 'ready':
      return `/projects/${project.id}`
  }
}

const NEXT_STEP: Record<Project['status'], string> = {
  draft: 'Enviar material',
  processing: 'Ver o progresso',
  failed: 'Ver o erro',
  ready: 'Abrir',
}

export function ProjectList() {
  const projects = useProjects()

  if (projects.isPending) {
    return (
      <div
        role="status"
        aria-label="Carregando projetos"
        className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
      >
        {[0, 1, 2].map((index) => (
          <div key={index} className="flex flex-col gap-3 rounded-lg border border-grey-200 p-6">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-6 w-3/4" />
            <Skeleton className="h-3.5 w-1/2" />
          </div>
        ))}
      </div>
    )
  }
  if (projects.isError) return <Alert tone="error">{errorMessage(projects.error)}</Alert>
  if (projects.data.length === 0) {
    return (
      <EmptyState
        icon="folder"
        title="Nenhum projeto ainda"
        action={<ButtonLink to="/projects/new">Criar o primeiro projeto</ButtonLink>}
      >
        Crie um projeto, envie o código e o documento da ideia, e o Fornalytics explica o produto em
        três lentes.
      </EmptyState>
    )
  }

  return (
    <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {projects.data.map((project) => (
        <li key={project.id}>
          <Link
            to={projectLink(project)}
            className="group flex h-full flex-col gap-4 rounded-lg border border-grey-200 bg-white p-6 transition-colors duration-150 hover:border-ink"
          >
            <div className="flex flex-wrap items-center gap-2">
              <ProjectStatusBadge status={project.status} />
              {project.base_outdated && (
                <span className="eyebrow text-warning">Material mudou</span>
              )}
            </div>
            <div className="flex flex-col gap-1">
              <span className="text-lg font-bold tracking-tight">{project.name}</span>
              <span className="text-[13px] text-grey-500">
                Criado em {formatDate(project.created_at)}
              </span>
            </div>
            <span className="mt-auto inline-flex items-center gap-2 text-sm font-semibold">
              {NEXT_STEP[project.status]}
              <Icon
                name="arrow"
                size={16}
                className="transition-transform duration-150 group-hover:translate-x-1"
              />
            </span>
          </Link>
        </li>
      ))}
    </ul>
  )
}

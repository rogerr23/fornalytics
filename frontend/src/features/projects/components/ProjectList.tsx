import { Link } from 'react-router-dom'
import { errorMessage } from '../../../shared/api/client'
import type { Project } from '../../../shared/api/projects'
import { formatDate } from '../../../shared/lib/format'
import { Alert } from '../../../shared/ui/Alert'
import { ProjectStatusBadge } from '../../../shared/ui/ProjectStatusBadge'
import { Spinner } from '../../../shared/ui/Spinner'
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

export function ProjectList() {
  const projects = useProjects()

  if (projects.isPending) return <Spinner label="Carregando projetos…" />
  if (projects.isError) return <Alert tone="error">{errorMessage(projects.error)}</Alert>
  if (projects.data.length === 0) {
    return (
      <p className="rounded-xl border border-dashed border-gray-300 p-8 text-center text-gray-500">
        Nenhum projeto ainda. Crie o primeiro para enviar o material de um produto.
      </p>
    )
  }

  return (
    <ul className="divide-y divide-gray-100 rounded-xl border border-gray-200 bg-white">
      {projects.data.map((project) => (
        <li key={project.id}>
          <Link
            to={projectLink(project)}
            className="flex items-center justify-between gap-4 px-5 py-4 hover:bg-gray-50"
          >
            <div className="flex flex-col">
              <span className="font-medium text-gray-900">{project.name}</span>
              <span className="text-xs text-gray-500">
                Criado em {formatDate(project.created_at)}
              </span>
            </div>
            <div className="flex items-center gap-2">
              {project.base_outdated && (
                <span className="text-xs text-amber-700">material mudou</span>
              )}
              <ProjectStatusBadge status={project.status} />
            </div>
          </Link>
        </li>
      ))}
    </ul>
  )
}

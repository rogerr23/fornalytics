import { useQuery } from '@tanstack/react-query'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useStartProcessing } from '../features/processing/hooks/useProcessing'
import { CreateProjectForm } from '../features/projects/components/CreateProjectForm'
import { MaterialEditor } from '../features/upload/components/MaterialEditor'
import { errorMessage } from '../shared/api/client'
import { projectQuery } from '../shared/api/projects'
import { Alert } from '../shared/ui/Alert'
import { Button } from '../shared/ui/Button'
import { Card } from '../shared/ui/Card'
import { Spinner } from '../shared/ui/Spinner'

/** Step 1 (name) at /projects/new; step 2 (material) at /projects/:id/material. */
export function NewProjectPage() {
  const { projectId } = useParams()
  const navigate = useNavigate()

  if (!projectId) {
    return (
      <>
        <h1 className="text-2xl font-bold text-gray-900">Novo projeto</h1>
        <Card>
          <CreateProjectForm
            onCreated={(project) => navigate(`/projects/${project.id}/material`)}
          />
        </Card>
      </>
    )
  }
  return <MaterialStep projectId={projectId} />
}

function MaterialStep({ projectId }: { projectId: string }) {
  const navigate = useNavigate()
  const project = useQuery(projectQuery(projectId))
  const start = useStartProcessing(projectId)

  if (project.isPending) return <Spinner label="Carregando o projeto…" />
  if (project.isError) return <Alert tone="error">{errorMessage(project.error)}</Alert>

  const detail = project.data
  const processed = detail.status === 'ready' || detail.base_outdated
  return (
    <>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm text-gray-500">
            <Link to="/" className="hover:underline">
              Projetos
            </Link>{' '}
            /{' '}
            {processed ? (
              <Link to={`/projects/${projectId}`} className="hover:underline">
                {detail.name}
              </Link>
            ) : (
              detail.name
            )}
          </p>
          <h1 className="text-2xl font-bold text-gray-900">Material do produto</h1>
        </div>
        <Button
          disabled={
            detail.sources.length === 0 || detail.status === 'processing' || start.isPending
          }
          onClick={() =>
            start.mutate(undefined, {
              onSuccess: () => navigate(`/projects/${projectId}/processing`),
            })
          }
        >
          {start.isPending ? 'Iniciando…' : processed ? 'Reprocessar' : 'Processar'}
        </Button>
      </div>
      {detail.status === 'processing' && (
        <Alert
          tone="info"
          title="O projeto está sendo processado"
          action={
            <Link to={`/projects/${projectId}/processing`}>
              <Button size="sm" variant="secondary">
                Ver o progresso
              </Button>
            </Link>
          }
        >
          O material não pode mudar até o processamento terminar.
        </Alert>
      )}
      {start.isError && <Alert tone="error">{errorMessage(start.error)}</Alert>}
      <MaterialEditor project={detail} />
    </>
  )
}

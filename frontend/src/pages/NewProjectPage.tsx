import { useQuery } from '@tanstack/react-query'
import { useNavigate, useParams } from 'react-router-dom'
import { useStartProcessing } from '../features/processing/hooks/useProcessing'
import { CreateProjectForm } from '../features/projects/components/CreateProjectForm'
import { MaterialEditor } from '../features/upload/components/MaterialEditor'
import { errorMessage } from '../shared/api/client'
import { projectQuery } from '../shared/api/projects'
import { Alert } from '../shared/ui/Alert'
import { Button, ButtonLink } from '../shared/ui/Button'
import { Card } from '../shared/ui/Card'
import { Icon } from '../shared/ui/Icon'
import { PageBody, PageHeader } from '../shared/ui/Page'
import { SkeletonText } from '../shared/ui/Skeleton'
import { JourneySteps } from '../shared/ui/Steps'

/** Step 1 (name) at /projects/new; step 2 (material) at /projects/:id/material. */
export function NewProjectPage() {
  const { projectId } = useParams()
  const navigate = useNavigate()

  if (!projectId) {
    return (
      <PageBody className="max-w-[720px]">
        <JourneySteps current={0} />
        <PageHeader
          crumbs={[{ label: 'Projetos', to: '/' }, { label: 'Novo projeto' }]}
          title={
            <>
              Novo <strong className="font-extrabold">projeto</strong>
            </>
          }
        />
        <Card>
          <CreateProjectForm
            onCreated={(project) => navigate(`/projects/${project.id}/material`)}
          />
        </Card>
      </PageBody>
    )
  }
  return <MaterialStep projectId={projectId} />
}

function MaterialStep({ projectId }: { projectId: string }) {
  const navigate = useNavigate()
  const project = useQuery(projectQuery(projectId))
  const start = useStartProcessing(projectId)

  if (project.isPending) {
    return (
      <PageBody>
        <SkeletonText lines={3} label="Carregando o projeto…" />
      </PageBody>
    )
  }
  if (project.isError) {
    return (
      <PageBody>
        <Alert tone="error">{errorMessage(project.error)}</Alert>
      </PageBody>
    )
  }

  const detail = project.data
  const processed = detail.status === 'ready' || detail.base_outdated
  return (
    <PageBody>
      {!processed && <JourneySteps current={1} />}
      <PageHeader
        crumbs={[
          { label: 'Projetos', to: '/' },
          { label: detail.name, to: processed ? `/projects/${projectId}` : undefined },
          { label: 'Material' },
        ]}
        title={
          <>
            Material do <strong className="font-extrabold">produto</strong>
          </>
        }
        description="Envie o código e, se tiver, o documento da ideia. Com os dois, o Fornalytics compara o que foi prometido com o que existe no código."
        actions={
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
            {!start.isPending && <Icon name="arrow" size={16} />}
          </Button>
        }
      />
      {detail.status === 'processing' && (
        <Alert
          tone="info"
          title="O projeto está sendo processado"
          action={
            <ButtonLink to={`/projects/${projectId}/processing`} size="sm" variant="secondary">
              Ver o progresso
            </ButtonLink>
          }
        >
          O material não pode mudar até o processamento terminar.
        </Alert>
      )}
      {start.isError && <Alert tone="error">{errorMessage(start.error)}</Alert>}
      <MaterialEditor project={detail} />
    </PageBody>
  )
}

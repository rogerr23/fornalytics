import { useQuery } from '@tanstack/react-query'
import { useCallback } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ProcessingView } from '../features/processing/components/ProcessingView'
import { projectQuery } from '../shared/api/projects'
import { PageBody, PageHeader } from '../shared/ui/Page'
import { JourneySteps } from '../shared/ui/Steps'

export function ProcessingPage() {
  const { projectId = '' } = useParams()
  const navigate = useNavigate()
  const project = useQuery(projectQuery(projectId))
  const onReady = useCallback(
    () => navigate(`/projects/${projectId}`, { replace: true }),
    [navigate, projectId],
  )

  return (
    <PageBody className="max-w-[880px]">
      <JourneySteps current={2} />
      <PageHeader
        crumbs={[{ label: 'Projetos', to: '/' }, { label: project.data?.name ?? '…' }]}
        title={
          <>
            Processando o <strong className="font-extrabold">material</strong>
          </>
        }
      />
      <ProcessingView projectId={projectId} onReady={onReady} />
    </PageBody>
  )
}

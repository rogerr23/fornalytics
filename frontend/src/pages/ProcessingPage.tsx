import { useQuery } from '@tanstack/react-query'
import { useCallback } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ProcessingView } from '../features/processing/components/ProcessingView'
import { projectQuery } from '../shared/api/projects'
import { useDocumentTitle } from '../shared/lib/useDocumentTitle'

export function ProcessingPage() {
  const { projectId = '' } = useParams()
  const navigate = useNavigate()
  const project = useQuery(projectQuery(projectId))
  useDocumentTitle('Processando', project.data?.name)
  const onReady = useCallback(
    () => navigate(`/projects/${projectId}`, { replace: true }),
    [navigate, projectId],
  )

  return (
    <>
      <div>
        <p className="text-sm text-gray-500">
          <Link to="/" className="hover:underline">
            Projetos
          </Link>{' '}
          / {project.data?.name ?? '…'}
        </p>
        <h1 className="text-2xl font-bold text-gray-900">Processando o material</h1>
      </div>
      <ProcessingView projectId={projectId} onReady={onReady} />
    </>
  )
}

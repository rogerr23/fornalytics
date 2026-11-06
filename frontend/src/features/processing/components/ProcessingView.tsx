import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { errorMessage } from '../../../shared/api/client'
import { Alert } from '../../../shared/ui/Alert'
import { Button } from '../../../shared/ui/Button'
import { Card } from '../../../shared/ui/Card'
import { Spinner } from '../../../shared/ui/Spinner'
import { useProcessingStatus, useStartProcessing } from '../hooks/useProcessing'

interface ProcessingViewProps {
  projectId: string
  onReady: () => void
}

/** Progress of the AI extraction, step by step, with a retry when it fails. */
export function ProcessingView({ projectId, onReady }: ProcessingViewProps) {
  const progress = useProcessingStatus(projectId)
  const start = useStartProcessing(projectId)
  const current = progress.data?.current
  const steps = progress.data?.steps ?? []
  const status = current?.status

  useEffect(() => {
    if (status === 'ready') onReady()
  }, [status, onReady])

  if (progress.isError) return <Alert tone="error">{errorMessage(progress.error)}</Alert>

  return (
    <Card className="flex flex-col gap-5">
      <ol className="flex flex-col gap-3">
        {steps.map((step, index) => {
          const running = status === 'processing' && index === steps.length - 1
          return (
            <li key={step} className="flex items-center gap-3 text-sm">
              {running ? (
                <Spinner />
              ) : (
                <span className="flex h-4 w-4 items-center justify-center rounded-full bg-green-500 text-[10px] text-white">
                  ✓
                </span>
              )}
              <span className={running ? 'font-medium text-gray-900' : 'text-gray-600'}>
                {step}
              </span>
            </li>
          )
        })}
        {!current && <Spinner label="Conectando…" />}
      </ol>

      {status === 'processing' && (
        <p className="text-xs text-gray-500">
          A IA lê o material e monta a base do produto. Pode levar alguns minutos; você pode fechar
          esta página e voltar depois.
        </p>
      )}

      {status === 'failed' && (
        <Alert
          tone="error"
          title="O processamento não terminou"
          action={
            <div className="flex gap-2">
              <Button size="sm" disabled={start.isPending} onClick={() => start.mutate()}>
                Tentar de novo
              </Button>
              <Link to={`/projects/${projectId}/material`}>
                <Button size="sm" variant="secondary">
                  Editar material
                </Button>
              </Link>
            </div>
          }
        >
          {current?.status_detail}
        </Alert>
      )}

      {status === 'draft' && (
        <Alert tone="info" title="Este projeto ainda não foi processado">
          <Link to={`/projects/${projectId}/material`} className="underline">
            Envie o material e clique em Processar.
          </Link>
        </Alert>
      )}

      {start.isError && <Alert tone="error">{errorMessage(start.error)}</Alert>}
    </Card>
  )
}

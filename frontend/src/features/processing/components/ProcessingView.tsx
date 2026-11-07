import { useEffect } from 'react'
import { errorMessage } from '../../../shared/api/client'
import { Alert } from '../../../shared/ui/Alert'
import { Button, ButtonLink } from '../../../shared/ui/Button'
import { Card } from '../../../shared/ui/Card'
import { Icon } from '../../../shared/ui/Icon'
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
    <Card className="flex flex-col gap-6">
      <ol className="flex flex-col">
        {steps.map((step, index) => {
          const running = status === 'processing' && index === steps.length - 1
          const failed = status === 'failed' && index === steps.length - 1
          const last = index === steps.length - 1
          return (
            <li key={step} className="relative flex gap-4 pb-6 last:pb-0">
              {!last && (
                <span
                  aria-hidden="true"
                  className="absolute top-8 bottom-0 left-[15px] w-px bg-grey-300"
                />
              )}
              <span
                className={`relative flex h-8 w-8 shrink-0 items-center justify-center rounded ${
                  running
                    ? 'border border-ink bg-white'
                    : failed
                      ? 'bg-danger text-white'
                      : 'bg-ink text-white'
                }`}
              >
                {running ? (
                  <span
                    aria-hidden="true"
                    className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-grey-200 border-t-ink"
                  />
                ) : (
                  <Icon name={failed ? 'close' : 'check'} size={16} />
                )}
              </span>
              <div className="flex flex-col pt-1">
                <span className="eyebrow text-grey-500">
                  Etapa {String(index + 1).padStart(2, '0')}
                </span>
                <span className={`text-sm ${running ? 'font-bold' : 'font-medium'}`}>{step}</span>
              </div>
            </li>
          )
        })}
        {!current && <Spinner label="Conectando…" />}
      </ol>

      {status === 'processing' && (
        <p className="border-t border-grey-200 pt-4 text-[13px] text-grey-500">
          A IA lê o material e monta a base do produto. Pode levar alguns minutos; você pode fechar
          esta página e voltar depois.
        </p>
      )}

      {status === 'failed' && (
        <Alert
          tone="error"
          title="O processamento não terminou"
          action={
            <div className="flex flex-wrap gap-2">
              <Button size="sm" disabled={start.isPending} onClick={() => start.mutate()}>
                <Icon name="refresh" size={16} />
                Tentar de novo
              </Button>
              <ButtonLink to={`/projects/${projectId}/material`} size="sm" variant="secondary">
                Editar material
              </ButtonLink>
            </div>
          }
        >
          {current?.status_detail}
        </Alert>
      )}

      {status === 'draft' && (
        <Alert
          tone="info"
          title="Este projeto ainda não foi processado"
          action={
            <ButtonLink to={`/projects/${projectId}/material`} size="sm" variant="secondary">
              Enviar material
            </ButtonLink>
          }
        >
          Envie o material e clique em Processar.
        </Alert>
      )}

      {start.isError && <Alert tone="error">{errorMessage(start.error)}</Alert>}
    </Card>
  )
}

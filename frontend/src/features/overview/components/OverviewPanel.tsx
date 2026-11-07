import { errorMessage } from '../../../shared/api/client'
import { LENS_LABEL, type Lens, type TextCitation } from '../../../shared/api/lens'
import { Alert } from '../../../shared/ui/Alert'
import { AnswerMarkdown } from '../../../shared/ui/AnswerMarkdown'
import { Button } from '../../../shared/ui/Button'
import { SkeletonText } from '../../../shared/ui/Skeleton'
import { Spinner } from '../../../shared/ui/Spinner'
import { useOverview } from '../hooks/useOverview'

interface OverviewPanelProps {
  projectId: string
  lens: Lens
  onOpenCitation: (citation: TextCitation) => void
}

export function OverviewPanel({ projectId, lens, onOpenCitation }: OverviewPanelProps) {
  const overview = useOverview(projectId, lens)
  const answer = overview.data

  if (overview.isError) {
    return (
      <Alert
        tone="error"
        action={
          <Button size="sm" variant="secondary" onClick={() => overview.refetch()}>
            Tentar de novo
          </Button>
        }
      >
        {errorMessage(overview.error)}
      </Alert>
    )
  }

  const streaming = overview.isFetching && !answer?.done
  return (
    <div className="flex flex-col gap-4">
      {(!answer || (!answer.text && !answer.error)) && (
        <div className="flex max-w-[72ch] flex-col gap-4">
          <Spinner label={`Escrevendo a visão geral na lente ${LENS_LABEL[lens]}…`} />
          <SkeletonText lines={5} label="Visão geral em preparação" />
        </div>
      )}
      {answer?.text && (
        <AnswerMarkdown
          text={answer.text}
          citations={answer.citations}
          onOpenCitation={onOpenCitation}
        />
      )}
      {streaming && answer?.text && <Spinner />}
      {answer?.error && (
        <Alert
          tone="error"
          action={
            <Button size="sm" variant="secondary" onClick={() => overview.refetch()}>
              Tentar de novo
            </Button>
          }
        >
          {answer.error}
        </Alert>
      )}
    </div>
  )
}

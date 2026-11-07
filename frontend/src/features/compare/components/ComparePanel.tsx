import { errorMessage } from '../../../shared/api/client'
import { LENSES, type TextCitation } from '../../../shared/api/lens'
import { useSessionHistory } from '../../../shared/api/sessionHistory'
import { Alert } from '../../../shared/ui/Alert'
import { AnswerMarkdown } from '../../../shared/ui/AnswerMarkdown'
import { QuestionForm } from '../../../shared/ui/QuestionForm'
import { Spinner } from '../../../shared/ui/Spinner'
import { useCompare } from '../hooks/useCompare'
import type { CompareResult } from '../types'

const SUGGESTIONS = [
  'O que este produto faz?',
  'Como funciona o fluxo principal?',
  'Quais limites o produto tem?',
]

interface ComparePanelProps {
  projectId: string
  onOpenCitation: (citation: TextCitation) => void
}

/** The same question in the three lenses: the form changes, the essence does not. */
export function ComparePanel({ projectId, onOpenCitation }: ComparePanelProps) {
  const compare = useCompare(projectId)
  const [results, addResult] = useSessionHistory<CompareResult>([
    'projects',
    projectId,
    'compare-history',
  ])

  return (
    <div className="flex flex-col gap-6">
      <p className="max-w-2xl text-sm text-grey-500">
        Uma pergunta, três explicações. As lentes mudam a forma, nunca a essência.
      </p>
      <QuestionForm
        placeholder="Faça uma pergunta para ver as três lentes lado a lado…"
        suggestions={SUGGESTIONS}
        busy={compare.isPending}
        busyLabel="Respondendo…"
        onAsk={(question) => compare.mutate(question, { onSuccess: addResult })}
      />
      {compare.isPending && <Spinner label="Escrevendo as três respostas…" />}
      {compare.isError && <Alert tone="error">{errorMessage(compare.error)}</Alert>}

      {results.map((result, index) => (
        <section key={`${index}-${result.question}`} className="flex flex-col gap-4">
          <h3 className="text-xl font-bold tracking-tight">{result.question}</h3>
          <div className="grid gap-6 lg:grid-cols-3">
            {LENSES.map(({ value, label, hint }, lensIndex) => {
              const answer = result.answers.find((item) => item.lens === value)
              return (
                <article key={value} className="flex flex-col gap-3 border-t border-ink pt-4">
                  <header className="flex items-baseline gap-3">
                    <span className="text-2xl font-bold text-grey-500">
                      {String(lensIndex + 1).padStart(2, '0')}
                    </span>
                    <div>
                      <p className="font-bold">{label}</p>
                      <p className="text-xs text-grey-500">{hint}</p>
                    </div>
                  </header>
                  {answer && (
                    <AnswerMarkdown
                      text={answer.text}
                      citations={answer.citations}
                      onOpenCitation={onOpenCitation}
                    />
                  )}
                </article>
              )
            })}
          </div>
        </section>
      ))}
    </div>
  )
}

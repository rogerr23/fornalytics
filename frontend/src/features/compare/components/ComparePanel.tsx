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
      <p className="text-sm text-gray-500">
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
        <section key={`${index}-${result.question}`} className="flex flex-col gap-3">
          <h3 className="font-semibold text-gray-900">{result.question}</h3>
          <div className="grid gap-4 lg:grid-cols-3">
            {LENSES.map(({ value, label, hint }) => {
              const answer = result.answers.find((item) => item.lens === value)
              return (
                <article
                  key={value}
                  className="flex flex-col gap-2 rounded-xl border border-gray-200 bg-white p-4"
                >
                  <header>
                    <p className="font-semibold text-indigo-700">{label}</p>
                    <p className="text-xs text-gray-500">{hint}</p>
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

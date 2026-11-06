import { errorMessage } from '../../../shared/api/client'
import { evidenceToCitation, type Lens, type TextCitation } from '../../../shared/api/lens'
import { useSessionHistory } from '../../../shared/api/sessionHistory'
import { citationLabel } from '../../../shared/lib/citations'
import { FEATURE_STATUS_TEXT } from '../../../shared/lib/featureStatus'
import { Alert } from '../../../shared/ui/Alert'
import { QuestionForm } from '../../../shared/ui/QuestionForm'
import { Spinner } from '../../../shared/ui/Spinner'
import { useDoesIt } from '../hooks/useDoesIt'
import type { DoesItResult } from '../types'
import { VERDICT_VIEW } from '../verdict'

const SUGGESTIONS = [
  'O produto tem login?',
  'Dá para exportar relatórios?',
  'Tem cupom de desconto?',
]

interface DoesItPanelProps {
  projectId: string
  lens: Lens
  onOpenCitation: (citation: TextCitation) => void
}

export function DoesItPanel({ projectId, lens, onOpenCitation }: DoesItPanelProps) {
  const ask = useDoesIt(projectId)
  const [results, addResult] = useSessionHistory<DoesItResult>([
    'projects',
    projectId,
    'does-it-history',
  ])

  return (
    <div className="flex flex-col gap-6">
      <p className="text-sm text-gray-500">
        Pergunte se o produto faz algo. A resposta segue o que a base encontrou no código e no
        documento da ideia.
      </p>
      <QuestionForm
        placeholder="Ex.: O sistema gera nota fiscal?"
        suggestions={SUGGESTIONS}
        busy={ask.isPending}
        busyLabel="Conferindo…"
        onAsk={(question) => ask.mutate({ question, lens }, { onSuccess: addResult })}
      />
      {ask.isPending && <Spinner label="Conferindo no material…" />}
      {ask.isError && <Alert tone="error">{errorMessage(ask.error)}</Alert>}

      {results.map((result, index) => (
        <VerdictCard
          key={`${index}-${result.question}`}
          result={result}
          onOpenCitation={onOpenCitation}
        />
      ))}
    </div>
  )
}

function VerdictCard({
  result,
  onOpenCitation,
}: {
  result: DoesItResult
  onOpenCitation: (citation: TextCitation) => void
}) {
  const view = VERDICT_VIEW[result.verdict]
  return (
    <article className="flex flex-col gap-3 rounded-xl border border-gray-200 bg-white p-5">
      <p className="text-sm text-gray-500">{result.question}</p>
      <div className={`flex items-center gap-3 rounded-lg border px-4 py-3 ${view.className}`}>
        <span className="text-2xl" aria-hidden>
          {view.icon}
        </span>
        <div>
          <p className="text-xl font-bold">{view.label}</p>
          {result.feature && (
            <p className="text-sm">
              {result.feature.name}: {FEATURE_STATUS_TEXT[result.feature.status]}
            </p>
          )}
        </div>
      </div>
      <p className="text-[15px] leading-relaxed text-gray-800">{result.justification}</p>
      {result.adjusted && (
        <p className="text-xs text-gray-500">
          A resposta foi ajustada para bater com a base do produto (a mesma do Ideia × Código).
        </p>
      )}
      {result.evidence.length > 0 && (
        <div className="flex flex-col gap-1.5">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Evidências</p>
          <ul className="flex flex-col gap-1.5">
            {result.evidence.map((evidence) => (
              <li key={`${evidence.path}:${evidence.line_start}`}>
                <button
                  type="button"
                  onClick={() => onOpenCitation(evidenceToCitation(evidence))}
                  className="flex w-full flex-col items-start gap-0.5 rounded-lg bg-gray-50 px-3 py-2 text-left hover:bg-indigo-50"
                >
                  <span className="font-mono text-xs text-indigo-700">
                    {citationLabel(evidence.path, evidence.line_start, evidence.line_end)}
                  </span>
                  <span className="font-mono text-xs text-gray-600">“{evidence.quote}”</span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </article>
  )
}

import { evidenceToCitation, type Evidence, type TextCitation } from '../../../shared/api/lens'
import { citationLabel } from '../../../shared/lib/citations'
import { Badge } from '../../../shared/ui/Badge'
import type { Flow } from '../types'
import { MermaidDiagram } from './MermaidDiagram'

interface FlowCardProps {
  flow: Flow
  onOpenCitation: (citation: TextCitation) => void
}

export function FlowCard({ flow, onOpenCitation }: FlowCardProps) {
  return (
    <article className="flex flex-col gap-4 rounded-xl border border-gray-200 bg-white p-5">
      <header className="flex flex-col gap-1">
        <div className="flex flex-wrap items-center gap-2">
          <h3 className="font-semibold text-gray-900">{flow.name}</h3>
          <Badge tone={flow.from_base ? 'gray' : 'indigo'}>
            {flow.from_base ? 'da base do produto' : 'gerado agora'}
          </Badge>
        </div>
        {flow.question && <p className="text-sm text-gray-500">{flow.question}</p>}
      </header>

      <div className="grid gap-5 lg:grid-cols-2">
        <MermaidDiagram text={flow.mermaid} />
        <div className="flex flex-col gap-3">
          {flow.steps.length === 0 ? (
            <p className="text-sm text-gray-600">Não encontrei esse fluxo no material.</p>
          ) : (
            <ol className="flex list-decimal flex-col gap-2 pl-5 text-sm text-gray-800">
              {flow.steps.map((step, index) => (
                <li key={index}>
                  {step.text}
                  <EvidenceChips evidence={step.evidence} onOpenCitation={onOpenCitation} />
                </li>
              ))}
            </ol>
          )}
          {flow.evidence.length > 0 && (
            <div className="flex flex-col gap-1">
              <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                Evidências
              </p>
              <EvidenceChips evidence={flow.evidence} onOpenCitation={onOpenCitation} />
            </div>
          )}
        </div>
      </div>
    </article>
  )
}

function EvidenceChips({
  evidence,
  onOpenCitation,
}: {
  evidence: Evidence[]
  onOpenCitation: (citation: TextCitation) => void
}) {
  if (evidence.length === 0) return null
  return (
    <span className="mt-1 flex flex-wrap gap-1.5">
      {evidence.map((item) => (
        <button
          key={`${item.path}:${item.line_start}`}
          type="button"
          title={`“${item.quote}”`}
          onClick={() => onOpenCitation(evidenceToCitation(item))}
          className="rounded bg-gray-50 px-1.5 py-0.5 font-mono text-xs text-indigo-700 ring-1 ring-gray-200 hover:bg-indigo-50"
        >
          {citationLabel(item.path, item.line_start, item.line_end)}
        </button>
      ))}
    </span>
  )
}

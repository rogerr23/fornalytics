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
    <article className="flex flex-col gap-5 rounded-lg border border-grey-200 bg-white p-6">
      <header className="flex flex-col gap-1">
        <div className="flex flex-wrap items-center gap-2">
          <h3 className="text-lg font-bold tracking-tight">{flow.name}</h3>
          <Badge tone={flow.from_base ? 'neutral' : 'ink'}>
            {flow.from_base ? 'da base do produto' : 'gerado agora'}
          </Badge>
        </div>
        {flow.question && <p className="text-sm text-grey-500">{flow.question}</p>}
      </header>

      <div className="grid gap-6 lg:grid-cols-2">
        <MermaidDiagram text={flow.mermaid} />
        <div className="flex flex-col gap-3">
          {flow.steps.length === 0 ? (
            <p className="text-sm text-grey-500">Não encontrei esse fluxo no material.</p>
          ) : (
            <ol className="flex flex-col text-sm text-ink-800">
              {flow.steps.map((step, index) => (
                <li
                  key={index}
                  className="flex gap-3 border-t border-grey-200 py-3 first:border-t-0 first:pt-0"
                >
                  <span className="w-7 shrink-0 text-base font-bold text-grey-500">
                    {String(index + 1).padStart(2, '0')}
                  </span>
                  <span className="flex flex-col">
                    {step.text}
                    <EvidenceChips evidence={step.evidence} onOpenCitation={onOpenCitation} />
                  </span>
                </li>
              ))}
            </ol>
          )}
          {flow.evidence.length > 0 && (
            <div className="flex flex-col gap-1">
              <p className="eyebrow text-grey-500">Evidências</p>
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
          className="rounded-sm border border-grey-300 bg-white px-1.5 py-0.5 font-mono text-xs text-ink transition-colors duration-150 hover:border-ink hover:bg-grey-100"
        >
          {citationLabel(item.path, item.line_start, item.line_end)}
        </button>
      ))}
    </span>
  )
}

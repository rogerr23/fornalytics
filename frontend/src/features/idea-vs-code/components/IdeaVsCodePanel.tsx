import { errorMessage } from '../../../shared/api/client'
import { evidenceToCitation, type TextCitation } from '../../../shared/api/lens'
import { citationLabel } from '../../../shared/lib/citations'
import { Alert } from '../../../shared/ui/Alert'
import { Badge } from '../../../shared/ui/Badge'
import { ButtonLink } from '../../../shared/ui/Button'
import { Skeleton } from '../../../shared/ui/Skeleton'
import { useIdeaVsCode } from '../hooks/useIdeaVsCode'
import { STATE_MESSAGE, summaryText } from '../summary'
import type { Feature } from '../types'

interface IdeaVsCodePanelProps {
  projectId: string
  onOpenCitation: (citation: TextCitation) => void
}

const COLUMNS = [
  {
    key: 'delivered' as const,
    number: '01',
    title: 'Prometido e implementado',
    empty: 'Nenhuma promessa encontrada no código.',
    dot: 'bg-success',
  },
  {
    key: 'missing' as const,
    number: '02',
    title: 'Prometido e não implementado',
    empty: 'Tudo o que foi prometido aparece no código.',
    dot: 'bg-warning',
  },
  {
    key: 'undocumented' as const,
    number: '03',
    title: 'Implementado e não documentado',
    empty: 'Nada além do que foi prometido.',
    dot: 'bg-info',
  },
]

/** The promise versus the code, straight from the product base (no AI call). */
export function IdeaVsCodePanel({ projectId, onOpenCitation }: IdeaVsCodePanelProps) {
  const result = useIdeaVsCode(projectId)

  if (result.isPending) {
    return (
      <div role="status" aria-label="Agrupando a base" className="grid gap-6 lg:grid-cols-3">
        {[0, 1, 2].map((index) => (
          <div key={index} className="flex flex-col gap-3">
            <Skeleton className="h-8 w-2/3" />
            <Skeleton className="h-28" />
            <Skeleton className="h-28" />
          </div>
        ))}
      </div>
    )
  }
  if (result.isError) return <Alert tone="error">{errorMessage(result.error)}</Alert>
  const data = result.data

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-1.5">
        <h2 className="text-2xl font-light tracking-tight sm:text-3xl">
          Ideia <strong className="font-extrabold">× Código</strong>
        </h2>
        {data.state === 'available' && (
          <p className="text-base font-semibold">{summaryText(data)}</p>
        )}
        <p className="max-w-2xl text-sm text-grey-500">
          Vem direto da base do produto, igual em todas as lentes. É a mesma informação que o "Isso
          faz?" usa.
        </p>
      </div>

      {data.state !== 'available' && (
        <Alert
          tone="info"
          title="Sem comparação completa"
          action={
            <ButtonLink to={`/projects/${projectId}/material`} size="sm" variant="secondary">
              Ver o material
            </ButtonLink>
          }
        >
          {STATE_MESSAGE[data.state]}
        </Alert>
      )}

      <div className="grid gap-8 lg:grid-cols-3 lg:gap-6">
        {COLUMNS.map((column) => {
          const features = data.columns[column.key]
          return (
            <section
              key={column.key}
              aria-labelledby={`col-${column.key}`}
              className="flex flex-col gap-3"
            >
              <header className="flex items-end gap-3 border-b border-ink pb-3 lg:min-h-[4.5rem]">
                <span className="text-3xl leading-none font-bold text-grey-500">
                  {column.number}
                </span>
                <h3 id={`col-${column.key}`} className="font-bold">
                  {column.title}
                </h3>
                <span className="ml-auto flex shrink-0 items-center gap-2 text-sm font-semibold">
                  <span aria-hidden="true" className={`h-2 w-2 rounded-full ${column.dot}`} />
                  {features.length}
                </span>
              </header>
              {features.length === 0 ? (
                <p className="py-2 text-sm text-grey-500">{column.empty}</p>
              ) : (
                <ul className="flex flex-col gap-3">
                  {features.map((feature) => (
                    <FeatureCard
                      key={`${feature.promise_ref}-${feature.name}`}
                      feature={feature}
                      onOpenCitation={onOpenCitation}
                    />
                  ))}
                </ul>
              )}
            </section>
          )
        })}
      </div>
    </div>
  )
}

function FeatureCard({
  feature,
  onOpenCitation,
}: {
  feature: Feature
  onOpenCitation: (citation: TextCitation) => void
}) {
  return (
    <li className="flex flex-col gap-2 rounded-lg border border-grey-200 bg-white p-5">
      <div className="flex flex-wrap items-center gap-2">
        <span className="font-bold">{feature.name}</span>
        {feature.status === 'partial' && <Badge tone="warning">Em parte</Badge>}
      </div>
      {feature.description && <p className="text-sm text-ink-600">{feature.description}</p>}
      {feature.evidence.length > 0 && (
        <div className="flex flex-wrap gap-1.5 pt-1">
          {feature.evidence.map((evidence) => (
            <button
              key={`${evidence.path}:${evidence.line_start}`}
              type="button"
              title={`“${evidence.quote}”`}
              onClick={() => onOpenCitation(evidenceToCitation(evidence))}
              className="rounded-sm border border-grey-300 bg-white px-1.5 py-0.5 font-mono text-xs text-ink transition-colors duration-150 hover:border-ink hover:bg-grey-100"
            >
              {citationLabel(evidence.path, evidence.line_start, evidence.line_end)}
            </button>
          ))}
        </div>
      )}
    </li>
  )
}

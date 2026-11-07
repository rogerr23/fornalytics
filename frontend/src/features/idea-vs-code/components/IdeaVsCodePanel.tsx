import { Link } from 'react-router-dom'
import { errorMessage } from '../../../shared/api/client'
import { evidenceToCitation, type TextCitation } from '../../../shared/api/lens'
import { citationLabel } from '../../../shared/lib/citations'
import { Alert } from '../../../shared/ui/Alert'
import { Badge } from '../../../shared/ui/Badge'
import { Spinner } from '../../../shared/ui/Spinner'
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
    icon: '✅',
    title: 'Prometido e implementado',
    empty: 'Nenhuma promessa encontrada no código.',
    accent: 'border-t-green-500',
  },
  {
    key: 'missing' as const,
    icon: '⚠️',
    title: 'Prometido e não implementado',
    empty: 'Tudo o que foi prometido aparece no código.',
    accent: 'border-t-amber-500',
  },
  {
    key: 'undocumented' as const,
    icon: '🔍',
    title: 'Implementado e não documentado',
    empty: 'Nada além do que foi prometido.',
    accent: 'border-t-indigo-500',
  },
]

/** The promise versus the code, straight from the product base (no AI call). */
export function IdeaVsCodePanel({ projectId, onOpenCitation }: IdeaVsCodePanelProps) {
  const result = useIdeaVsCode(projectId)

  if (result.isPending) return <Spinner label="Agrupando a base…" />
  if (result.isError) return <Alert tone="error">{errorMessage(result.error)}</Alert>
  const data = result.data

  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-col gap-1">
        {data.state === 'available' && (
          <p className="text-lg font-semibold text-gray-900">{summaryText(data)}</p>
        )}
        <p className="text-sm text-gray-500">
          Vem direto da base do produto, igual em todas as lentes. É a mesma informação que o "Isso
          faz?" usa.
        </p>
      </div>

      {data.state !== 'available' && (
        <Alert
          tone="info"
          title="Sem comparação completa"
          action={
            <Link to={`/projects/${projectId}/material`} className="text-sm underline">
              Ver o material
            </Link>
          }
        >
          {STATE_MESSAGE[data.state]}
        </Alert>
      )}

      <div className="grid gap-4 lg:grid-cols-3">
        {COLUMNS.map((column) => {
          const features = data.columns[column.key]
          return (
            <section
              key={column.key}
              className={`flex flex-col gap-3 rounded-xl border border-t-4 border-gray-200 bg-white p-4 ${column.accent}`}
            >
              <header className="flex items-center justify-between gap-2">
                <h3 className="flex gap-1.5 font-semibold text-gray-900">
                  <span aria-hidden>{column.icon}</span>
                  <span>{column.title}</span>
                </h3>
                <Badge>{features.length}</Badge>
              </header>
              {features.length === 0 ? (
                <p className="text-sm text-gray-500">
                  {data.state === 'available' ? column.empty : 'Sem promessas para comparar.'}
                </p>
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
    <li className="flex flex-col gap-1.5 rounded-lg bg-gray-50 p-3">
      <div className="flex flex-wrap items-center gap-2">
        <span className="font-medium text-gray-900">{feature.name}</span>
        {feature.status === 'partial' && <Badge tone="amber">em parte</Badge>}
      </div>
      {feature.description && <p className="text-sm text-gray-700">{feature.description}</p>}
      {feature.evidence.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {feature.evidence.map((evidence) => (
            <button
              key={`${evidence.path}:${evidence.line_start}`}
              type="button"
              title={`“${evidence.quote}”`}
              onClick={() => onOpenCitation(evidenceToCitation(evidence))}
              className="rounded bg-white px-1.5 py-0.5 font-mono text-xs text-indigo-700 ring-1 ring-gray-200 hover:bg-indigo-50"
            >
              {citationLabel(evidence.path, evidence.line_start, evidence.line_end)}
            </button>
          ))}
        </div>
      )}
    </li>
  )
}

import { useState } from 'react'
import { errorMessage } from '../../../shared/api/client'
import { SOURCE_TYPE_LABEL, type ProjectDetail } from '../../../shared/api/projects'
import { formatTokens, plural } from '../../../shared/lib/format'
import { Alert } from '../../../shared/ui/Alert'
import { Button } from '../../../shared/ui/Button'
import { Card } from '../../../shared/ui/Card'
import { useDeleteSource } from '../hooks/useSources'
import type { IngestionSummary } from '../types'
import { IngestionSummaryView } from './IngestionSummaryView'
import { LimitsWarning } from './LimitsWarning'
import { SourceUploader } from './SourceUploader'

/** Upload, review and remove the material of a project. */
export function MaterialEditor({ project }: { project: ProjectDetail }) {
  // Summaries of what was sent in this visit (the API returns them only on upload).
  const [summaries, setSummaries] = useState<Record<string, IngestionSummary>>({})
  const remove = useDeleteSource(project.id)
  const locked = project.status === 'processing'

  return (
    <div className="flex flex-col gap-5">
      <Card>
        <h2 className="mb-3 font-semibold text-gray-900">Adicionar material</h2>
        <SourceUploader
          projectId={project.id}
          disabled={locked}
          onUploaded={(summary) =>
            setSummaries((current) => ({ ...current, [summary.source_id]: summary }))
          }
        />
      </Card>

      <Card>
        <h2 className="mb-3 font-semibold text-gray-900">
          Material do projeto{' '}
          <span className="font-normal text-gray-500">({project.sources.length})</span>
        </h2>
        {project.sources.length === 0 ? (
          <p className="text-sm text-gray-500">
            Envie o código (.zip) e, se tiver, o documento da ideia. Com os dois, o Fornalytics
            compara o que foi prometido com o que existe no código.
          </p>
        ) : (
          <ul className="flex flex-col gap-3">
            {project.sources.map((source) => (
              <li
                key={source.id}
                className="flex flex-col gap-2 border-b border-gray-100 pb-3 last:border-0 last:pb-0"
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="flex flex-col">
                    <span className="font-medium text-gray-900">
                      {source.filename ?? 'Texto colado'}
                    </span>
                    <span className="text-xs text-gray-500">
                      {SOURCE_TYPE_LABEL[source.type]} · {plural(source.file_count, 'arquivo')} ·{' '}
                      {formatTokens(source.token_estimate)}
                    </span>
                  </div>
                  <Button
                    variant="danger"
                    size="sm"
                    disabled={locked || remove.isPending}
                    onClick={() => remove.mutate(source.id)}
                  >
                    Remover
                  </Button>
                </div>
                {summaries[source.id] && <IngestionSummaryView summary={summaries[source.id]} />}
              </li>
            ))}
          </ul>
        )}
        {remove.isError && (
          <div className="mt-3">
            <Alert tone="error">{errorMessage(remove.error)}</Alert>
          </div>
        )}
      </Card>

      <LimitsWarning limits={project.limits} />
    </div>
  )
}

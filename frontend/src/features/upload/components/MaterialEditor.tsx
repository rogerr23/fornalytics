import { useState } from 'react'
import { errorMessage } from '../../../shared/api/client'
import { SOURCE_TYPE_LABEL, type ProjectDetail, type Source } from '../../../shared/api/projects'
import { formatTokens, plural } from '../../../shared/lib/format'
import { Alert } from '../../../shared/ui/Alert'
import { Button } from '../../../shared/ui/Button'
import { Card, CardTitle } from '../../../shared/ui/Card'
import { Icon, type IconName } from '../../../shared/ui/Icon'
import { useDeleteSource } from '../hooks/useSources'
import type { IngestionSummary } from '../types'
import { IngestionSummaryView } from './IngestionSummaryView'
import { LimitsWarning } from './LimitsWarning'
import { SourceUploader } from './SourceUploader'

function sourceIcon(source: Source): IconName {
  if (source.type === 'code') return source.filename?.startsWith('github.com/') ? 'link' : 'folder'
  return source.filename ? 'file' : 'text'
}

/** Upload, review and remove the material of a project. */
export function MaterialEditor({ project }: { project: ProjectDetail }) {
  // Summaries of what was sent in this visit (the API returns them only on upload).
  const [summaries, setSummaries] = useState<Record<string, IngestionSummary>>({})
  const remove = useDeleteSource(project.id)
  const locked = project.status === 'processing'

  return (
    <div className="grid grid-cols-[minmax(0,1fr)] items-start gap-6 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,1fr)]">
      <Card>
        <CardTitle>Adicionar material</CardTitle>
        <SourceUploader
          projectId={project.id}
          disabled={locked}
          onUploaded={(summary) =>
            setSummaries((current) => ({ ...current, [summary.source_id]: summary }))
          }
        />
      </Card>

      <div className="flex flex-col gap-6">
        <Card>
          <CardTitle count={project.sources.length}>Material do projeto</CardTitle>
          {project.sources.length === 0 ? (
            <p className="text-sm text-grey-500">
              Nada enviado ainda. O código pode ir como .zip ou link do GitHub; o documento da
              ideia, como PDF, DOCX, MD, TXT ou texto colado.
            </p>
          ) : (
            <ul className="flex flex-col">
              {project.sources.map((source) => (
                <li
                  key={source.id}
                  className="flex flex-col gap-3 border-t border-grey-200 py-4 first:border-t-0 first:pt-0 last:pb-0"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex min-w-0 items-start gap-3">
                      <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded border border-grey-200">
                        <Icon name={sourceIcon(source)} size={18} />
                      </span>
                      <div className="flex min-w-0 flex-col">
                        <span className="truncate font-semibold">
                          {source.filename ?? 'Texto colado'}
                        </span>
                        <span className="text-[13px] text-grey-500">
                          {SOURCE_TYPE_LABEL[source.type]} · {plural(source.file_count, 'arquivo')}{' '}
                          · {formatTokens(source.token_estimate)}
                        </span>
                      </div>
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
            <div className="mt-4">
              <Alert tone="error">{errorMessage(remove.error)}</Alert>
            </div>
          )}
        </Card>
        <LimitsWarning limits={project.limits} />
      </div>
    </div>
  )
}

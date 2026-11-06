import { formatTokens, plural } from '../../../shared/lib/format'
import { SKIP_LABEL, type IngestionSummary } from '../types'

/** What happened to one upload: files used, ignored (grouped by reason) and renamed. */
export function IngestionSummaryView({ summary }: { summary: IngestionSummary }) {
  return (
    <div className="flex flex-col gap-2 rounded-lg bg-gray-50 p-3 text-sm text-gray-700">
      <p>
        <span className="font-medium text-gray-900">{plural(summary.files.length, 'arquivo')}</span>{' '}
        lido{summary.files.length === 1 ? '' : 's'} · {formatTokens(summary.token_estimate)}
      </p>
      {summary.skipped.length > 0 && (
        <details>
          <summary className="cursor-pointer text-gray-600">
            {plural(
              summary.skipped.reduce((total, group) => total + group.count, 0),
              'arquivo ignorado',
              'arquivos ignorados',
            )}
          </summary>
          <ul className="mt-1 flex flex-col gap-1 pl-4">
            {summary.skipped.map((group) => (
              <li key={group.reason}>
                {group.count} {SKIP_LABEL[group.reason]}
                <span className="block truncate font-mono text-xs text-gray-500">
                  {group.examples.join(', ')}
                  {group.count > group.examples.length ? ', …' : ''}
                </span>
              </li>
            ))}
          </ul>
        </details>
      )}
      {summary.renamed.length > 0 && (
        <p className="text-xs text-gray-600">
          Nomes repetidos no projeto:{' '}
          {summary.renamed.map((item) => `${item.original} → ${item.stored_as}`).join('; ')}
        </p>
      )}
    </div>
  )
}

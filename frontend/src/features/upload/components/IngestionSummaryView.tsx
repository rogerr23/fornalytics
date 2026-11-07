import { formatTokens, plural } from '../../../shared/lib/format'
import { SKIP_LABEL, type IngestionSummary } from '../types'

/** What happened to one upload: files used, ignored (grouped by reason) and renamed. */
export function IngestionSummaryView({ summary }: { summary: IngestionSummary }) {
  const skipped = summary.skipped.reduce((total, group) => total + group.count, 0)
  return (
    <div className="flex flex-col gap-3 rounded border border-grey-200 bg-grey-50 p-4 text-sm">
      <div className="flex flex-wrap gap-x-8 gap-y-2">
        <Figure
          value={String(summary.files.length)}
          label={summary.files.length === 1 ? 'arquivo lido' : 'arquivos lidos'}
        />
        <Figure
          value={formatTokens(summary.token_estimate).replace(' tokens', '')}
          label="tokens"
        />
        {skipped > 0 && (
          <Figure value={String(skipped)} label={skipped === 1 ? 'ignorado' : 'ignorados'} />
        )}
      </div>
      {summary.skipped.length > 0 && (
        <details className="group">
          <summary className="cursor-pointer text-[13px] font-semibold underline-offset-4 hover:underline">
            Ver o que foi ignorado
          </summary>
          <ul className="mt-2 flex flex-col gap-2">
            {summary.skipped.map((group) => (
              <li key={group.reason} className="text-[13px]">
                {plural(group.count, 'arquivo')} · {SKIP_LABEL[group.reason]}
                <span className="block truncate font-mono text-xs text-grey-500">
                  {group.examples.join(', ')}
                  {group.count > group.examples.length ? ', …' : ''}
                </span>
              </li>
            ))}
          </ul>
        </details>
      )}
      {summary.renamed.length > 0 && (
        <p className="text-xs text-grey-500">
          Nomes repetidos no projeto:{' '}
          {summary.renamed.map((item) => `${item.original} → ${item.stored_as}`).join('; ')}
        </p>
      )}
    </div>
  )
}

function Figure({ value, label }: { value: string; label: string }) {
  return (
    <span className="flex items-baseline gap-1.5">
      <span className="text-2xl font-bold tracking-tight text-grey-500">{value}</span>
      <span className="text-[13px]">{label}</span>
    </span>
  )
}

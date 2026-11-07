import type { Limits } from '../../../shared/api/projects'
import { formatTokens } from '../../../shared/lib/format'
import { Alert } from '../../../shared/ui/Alert'

/** Material above MAX_CONTEXT_TOKENS enters by priority; what stays out is listed, never silent. */
export function LimitsWarning({ limits }: { limits: Limits }) {
  const groups = [
    { label: 'Documentos', group: limits.documents },
    { label: 'Código', group: limits.code },
  ].filter(({ group }) => group.excluded.length > 0)

  if (groups.length === 0) return null

  return (
    <Alert tone="warning" title="Parte do material fica de fora do processamento">
      <p>
        Cada etapa aceita até {formatTokens(limits.budget_per_step)}. Os arquivos entram por
        prioridade (README, rotas, modelos, serviços…) e estes ficam de fora:
      </p>
      {groups.map(({ label, group }) => (
        <details key={label} className="mt-2">
          <summary className="cursor-pointer font-semibold text-ink">
            {label}: {group.excluded.length} de fora ({formatTokens(group.total_tokens)} no total)
          </summary>
          <ul className="mt-2 max-h-40 overflow-y-auto rounded border border-grey-200 bg-white p-3 font-mono text-xs">
            {group.excluded.map((file) => (
              <li key={file.path}>{file.path}</li>
            ))}
          </ul>
        </details>
      ))}
    </Alert>
  )
}

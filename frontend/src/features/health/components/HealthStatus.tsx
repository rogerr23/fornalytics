import { useHealth, type DatabaseStatus, type LLMStatus } from '../../../shared/api/health'

interface StatusView {
  label: string
  color: string
}

const OK = 'bg-success'
const WARN = 'bg-warning'
const BAD = 'bg-danger'

const DATABASE_STATUS: Record<DatabaseStatus, StatusView> = {
  ok: { label: 'ok', color: OK },
  unavailable: { label: 'sem conexão', color: BAD },
  not_configured: { label: 'não configurado (.env)', color: WARN },
}

const PROVIDER_LABEL: Record<LLMStatus['provider'], string> = { gemini: 'Gemini', ollama: 'Ollama' }

function llmView(llm: LLMStatus): StatusView {
  const name = PROVIDER_LABEL[llm.provider]
  return llm.configured
    ? { label: `${name} · ${llm.model}`, color: OK }
    : { label: `${name} não configurada (.env)`, color: WARN }
}

const CHECKING: StatusView = { label: 'verificando…', color: 'bg-grey-300' }
const DOWN: StatusView = { label: 'fora do ar', color: BAD }

function StatusDot({ name, view }: { name: string; view: StatusView }) {
  return (
    // Only the dot is visible; the detail stays in the tooltip and for screen readers.
    <span className="flex cursor-default items-center gap-2" title={`${name}: ${view.label}`}>
      <span aria-hidden="true" className={`inline-block h-2 w-2 rounded-full ${view.color}`} />
      <span className="eyebrow text-grey-500">{name}</span>
      <span className="sr-only">{view.label}</span>
    </span>
  )
}

/** Backend, database and AI status in one discreet line (no model call, no quota used). */
export function HealthStatus() {
  const health = useHealth()
  const pick = (ok: () => StatusView) =>
    health.isPending ? CHECKING : health.isSuccess ? ok() : DOWN

  return (
    <div className="flex flex-wrap gap-x-6 gap-y-2 text-xs text-ink-600">
      <StatusDot name="API" view={pick(() => ({ label: 'ok', color: OK }))} />
      <StatusDot name="Banco" view={pick(() => DATABASE_STATUS[health.data!.database])} />
      <StatusDot name="IA" view={pick(() => llmView(health.data!.llm))} />
    </div>
  )
}

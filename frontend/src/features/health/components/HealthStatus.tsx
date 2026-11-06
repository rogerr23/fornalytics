import { useHealth, type DatabaseStatus, type LLMStatus } from '../../../shared/api/health'

interface StatusView {
  label: string
  color: string
}

const DATABASE_STATUS: Record<DatabaseStatus, StatusView> = {
  ok: { label: 'ok', color: 'bg-green-500' },
  unavailable: { label: 'sem conexão', color: 'bg-red-500' },
  not_configured: { label: 'não configurado (.env)', color: 'bg-yellow-500' },
}

const PROVIDER_LABEL: Record<LLMStatus['provider'], string> = { gemini: 'Gemini', ollama: 'Ollama' }

function llmView(llm: LLMStatus): StatusView {
  const name = PROVIDER_LABEL[llm.provider]
  return llm.configured
    ? { label: `${name} · ${llm.model}`, color: 'bg-green-500' }
    : { label: `${name} não configurada (.env)`, color: 'bg-yellow-500' }
}

const CHECKING: StatusView = { label: 'verificando…', color: 'bg-gray-400' }
const DOWN: StatusView = { label: 'fora do ar', color: 'bg-red-500' }

function StatusDot({ name, view }: { name: string; view: StatusView }) {
  return (
    <span className="flex items-center gap-1.5">
      <span className={`inline-block h-2 w-2 rounded-full ${view.color}`} />
      {name}: {view.label}
    </span>
  )
}

/** Backend, database and AI status in one discreet line (no model call, no quota used). */
export function HealthStatus() {
  const health = useHealth()
  const pick = (ok: () => StatusView) =>
    health.isPending ? CHECKING : health.isSuccess ? ok() : DOWN

  return (
    <div className="flex flex-wrap gap-x-5 gap-y-1 text-xs text-gray-500">
      <StatusDot name="API" view={pick(() => ({ label: 'ok', color: 'bg-green-500' }))} />
      <StatusDot name="Banco" view={pick(() => DATABASE_STATUS[health.data!.database])} />
      <StatusDot name="IA" view={pick(() => llmView(health.data!.llm))} />
    </div>
  )
}

import { useHealth, type DatabaseStatus } from '../shared/api/health'

interface StatusView {
  label: string
  color: string
}

const DATABASE_STATUS: Record<DatabaseStatus, StatusView> = {
  ok: { label: 'ok', color: 'bg-green-500' },
  unavailable: { label: 'sem conexão', color: 'bg-red-500' },
  not_configured: { label: 'não configurado (.env)', color: 'bg-yellow-500' },
}

const CHECKING: StatusView = { label: 'verificando…', color: 'bg-gray-400' }
const DOWN: StatusView = { label: 'fora do ar', color: 'bg-red-500' }

function StatusLine({ name, view }: { name: string; view: StatusView }) {
  return (
    <p className="flex items-center gap-2 text-sm text-gray-700">
      <span className={`inline-block h-2.5 w-2.5 rounded-full ${view.color}`} />
      {name}: {view.label}
    </p>
  )
}

// Temporary home page. The real project list arrives in Phase 6.
export function ProjectsPage() {
  const health = useHealth()

  const backend = health.isPending
    ? CHECKING
    : health.isSuccess
      ? { label: `ok (v${health.data.version})`, color: 'bg-green-500' }
      : DOWN
  const database = health.isPending
    ? CHECKING
    : health.isSuccess
      ? DATABASE_STATUS[health.data.database]
      : DOWN

  return (
    <main className="mx-auto flex min-h-screen max-w-2xl flex-col justify-center gap-4 p-8">
      <h1 className="text-4xl font-bold text-gray-900">Fornalytics</h1>
      <p className="text-gray-600">Um produto, várias explicações.</p>
      <div className="flex flex-col gap-1">
        <StatusLine name="Backend" view={backend} />
        <StatusLine name="Banco" view={database} />
      </div>
    </main>
  )
}

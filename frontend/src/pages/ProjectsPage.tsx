import { useHealth } from '../shared/api/health'

// Temporary home page for Phase 0. The real project list arrives in Phase 6.
export function ProjectsPage() {
  const health = useHealth()

  const status = health.isPending
    ? { label: 'verificando…', color: 'bg-gray-400' }
    : health.isSuccess
      ? { label: `ok (v${health.data.version})`, color: 'bg-green-500' }
      : { label: 'fora do ar', color: 'bg-red-500' }

  return (
    <main className="mx-auto flex min-h-screen max-w-2xl flex-col justify-center gap-4 p-8">
      <h1 className="text-4xl font-bold text-gray-900">Fornalytics</h1>
      <p className="text-gray-600">Um produto, várias explicações.</p>
      <p className="flex items-center gap-2 text-sm text-gray-700">
        <span className={`inline-block h-2.5 w-2.5 rounded-full ${status.color}`} />
        Backend: {status.label}
      </p>
    </main>
  )
}

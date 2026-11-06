import { Link, Outlet } from 'react-router-dom'

export function Layout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-3">
          <Link to="/" className="text-lg font-bold text-gray-900">
            Fornalytics
          </Link>
          <span className="text-sm text-gray-500">Um produto, várias explicações</span>
        </div>
      </header>
      <main className="mx-auto flex max-w-5xl flex-col gap-6 px-6 py-8">
        <Outlet />
      </main>
    </div>
  )
}

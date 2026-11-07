import { Link, NavLink, Outlet } from 'react-router-dom'
import extremeMark from '../assets/extreme-x.png'

const NAV_LINK = ({ isActive }: { isActive: boolean }) =>
  `inline-flex min-h-11 items-center border-b-2 text-sm font-semibold transition-colors duration-150 ${
    isActive ? 'border-ink text-ink' : 'border-transparent text-grey-500 hover:text-ink'
  }`

export function Layout() {
  return (
    <div className="flex min-h-screen flex-col bg-white">
      <a
        href="#conteudo"
        className="sr-only z-50 bg-ink px-4 py-2 text-white focus:not-sr-only focus:fixed focus:top-2 focus:left-2"
      >
        Pular para o conteúdo
      </a>
      <header className="sticky top-0 z-10 border-b border-grey-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-[1240px] flex-wrap items-center justify-between gap-x-6 gap-y-1 px-4 py-2 sm:px-8">
          <Link to="/" className="flex min-h-11 items-center gap-3">
            <img src={extremeMark} alt="" className="h-6 w-6 object-contain" />
            <span className="text-lg font-extrabold tracking-tight">Fornalytics</span>
            <span className="eyebrow hidden border-l border-grey-300 pl-3 text-grey-500 md:inline">
              Programa de Estágio Extreme Group
            </span>
          </Link>
          <nav aria-label="Principal" className="flex gap-6">
            <NavLink to="/" end className={NAV_LINK}>
              Projetos
            </NavLink>
            <NavLink to="/projects/new" end className={NAV_LINK}>
              Novo projeto
            </NavLink>
          </nav>
        </div>
      </header>
      <main id="conteudo" className="flex flex-1 flex-col">
        <Outlet />
      </main>
    </div>
  )
}

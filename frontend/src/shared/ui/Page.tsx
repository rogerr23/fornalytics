import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'

/** Standard page body: max width, gutters and vertical rhythm. */
export function PageBody({
  children,
  className = '',
}: {
  children: ReactNode
  className?: string
}) {
  return (
    <div
      className={`mx-auto flex w-full max-w-[1240px] flex-col gap-8 px-4 py-8 sm:px-8 sm:py-10 ${className}`}
    >
      {children}
    </div>
  )
}

export interface Crumb {
  label: string
  to?: string
}

export function Breadcrumbs({ items, inverse = false }: { items: Crumb[]; inverse?: boolean }) {
  const muted = inverse ? 'text-grey-300' : 'text-grey-500'
  return (
    <nav aria-label="Caminho" className={`eyebrow flex flex-wrap items-center gap-2 ${muted}`}>
      {items.map((item, index) => (
        <span key={`${item.label}-${index}`} className="flex items-center gap-2">
          {index > 0 && <span aria-hidden="true">/</span>}
          {item.to ? (
            <Link
              to={item.to}
              className={`underline-offset-4 hover:underline ${inverse ? 'hover:text-white' : 'hover:text-ink'}`}
            >
              {item.label}
            </Link>
          ) : (
            <span aria-current="page">{item.label}</span>
          )}
        </span>
      ))}
    </nav>
  )
}

interface PageHeaderProps {
  crumbs?: Crumb[]
  title: ReactNode
  description?: ReactNode
  actions?: ReactNode
}

/** Title block of a page: breadcrumbs, title with the brand's weight split, actions. */
export function PageHeader({ crumbs, title, description, actions }: PageHeaderProps) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-x-8 gap-y-4">
      <div className="flex min-w-0 flex-col gap-2">
        {crumbs && <Breadcrumbs items={crumbs} />}
        <h1 className="text-3xl leading-tight font-light tracking-tight sm:text-4xl">{title}</h1>
        {description && <p className="max-w-2xl text-grey-500">{description}</p>}
      </div>
      {actions && <div className="flex flex-wrap items-center gap-3">{actions}</div>}
    </div>
  )
}

/** Full-bleed black band for hero moments (project header). */
export function HeroBand({ children }: { children: ReactNode }) {
  return (
    <section className="on-dark bg-ink text-white">
      <div className="mx-auto flex w-full max-w-[1240px] flex-col gap-8 px-4 py-10 sm:px-8 sm:py-12">
        {children}
      </div>
    </section>
  )
}

/** Large steel numeral with a label whose first word is bold, as in the brand's statistics. */
export function Stat({
  value,
  strong,
  rest,
  inverse = false,
}: {
  value: string
  strong: string
  rest: string
  inverse?: boolean
}) {
  return (
    <div className="flex flex-col gap-1">
      <span
        className={`text-4xl leading-none font-bold tracking-tight sm:text-5xl ${inverse ? 'text-grey-400' : 'text-grey-500'}`}
      >
        {value}
      </span>
      <span className={`text-[13px] ${inverse ? 'text-white' : 'text-ink'}`}>
        <strong className="font-bold">{strong}</strong> {rest}
      </span>
    </div>
  )
}

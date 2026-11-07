import type { ReactNode } from 'react'

/** A 1px hairline on white, 8px corners, no shadow (structure comes from rules, not lift). */
export function Card({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <section className={`rounded-lg border border-grey-200 bg-white p-6 ${className}`}>
      {children}
    </section>
  )
}

/** Card heading: uppercase eyebrow plus an optional count. */
export function CardTitle({ children, count }: { children: ReactNode; count?: number }) {
  return (
    <h2 className="mb-4 flex items-baseline gap-2 text-base font-bold">
      {children}
      {count !== undefined && <span className="font-medium text-grey-500">{count}</span>}
    </h2>
  )
}

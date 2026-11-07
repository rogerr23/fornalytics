import type { ReactNode } from 'react'

type Tone = 'neutral' | 'success' | 'warning' | 'danger' | 'info' | 'ink'

const TONES: Record<Tone, string> = {
  neutral: 'bg-grey-100 text-ink-600',
  success: 'bg-success-tint text-success',
  warning: 'bg-warning-tint text-warning',
  danger: 'bg-danger-tint text-danger',
  info: 'bg-info-tint text-info',
  ink: 'bg-ink text-white',
}

/** Pill tag: the only rounded-full shape in the system. */
export function Badge({ tone = 'neutral', children }: { tone?: Tone; children: ReactNode }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[11px] font-semibold tracking-[0.04em] uppercase ${TONES[tone]}`}
    >
      {children}
    </span>
  )
}

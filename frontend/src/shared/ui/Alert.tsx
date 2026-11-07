import type { ReactNode } from 'react'
import { Icon, type IconName } from './Icon'

type Tone = 'info' | 'warning' | 'error' | 'success'

const TONES: Record<Tone, { box: string; icon: IconName; color: string }> = {
  info: { box: 'border-grey-300 bg-grey-50', icon: 'info', color: 'text-ink' },
  warning: { box: 'border-warning/30 bg-warning-tint', icon: 'alert', color: 'text-warning' },
  error: { box: 'border-danger/30 bg-danger-tint', icon: 'alert', color: 'text-danger' },
  success: { box: 'border-success/30 bg-success-tint', icon: 'check', color: 'text-success' },
}

interface AlertProps {
  tone?: Tone
  title?: string
  children?: ReactNode
  action?: ReactNode
}

export function Alert({ tone = 'info', title, children, action }: AlertProps) {
  const view = TONES[tone]
  return (
    <div
      role={tone === 'error' ? 'alert' : 'status'}
      className={`flex flex-wrap items-start gap-x-4 gap-y-3 rounded-lg border px-4 py-3.5 text-sm text-ink ${view.box}`}
    >
      <Icon name={view.icon} className={`mt-0.5 shrink-0 ${view.color}`} />
      <div className="flex min-w-0 flex-1 basis-60 flex-col gap-1">
        {title && <p className="font-bold">{title}</p>}
        {children && <div className="text-ink-600">{children}</div>}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  )
}

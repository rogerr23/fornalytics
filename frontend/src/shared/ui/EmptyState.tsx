import type { ReactNode } from 'react'
import { Icon, type IconName } from './Icon'

interface EmptyStateProps {
  icon: IconName
  title: string
  children?: ReactNode
  action?: ReactNode
}

/** What a screen shows when there is nothing yet: what it is for and the next step. */
export function EmptyState({ icon, title, children, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-start gap-3 rounded-lg border border-dashed border-grey-300 px-6 py-10 sm:items-center sm:text-center">
      <span className="flex h-11 w-11 items-center justify-center rounded border border-grey-200">
        <Icon name={icon} size={22} />
      </span>
      <p className="text-base font-bold">{title}</p>
      {children && <div className="max-w-md text-sm text-grey-500">{children}</div>}
      {action && <div className="pt-1">{action}</div>}
    </div>
  )
}

import type { IconName } from '../../shared/ui/Icon'
import type { Verdict } from './types'

export const VERDICT_VIEW: Record<Verdict, { label: string; icon: IconName; className: string }> = {
  sim: { label: 'Sim', icon: 'check', className: 'border-success/30 bg-success-tint text-success' },
  parcialmente: {
    label: 'Parcialmente',
    icon: 'minus',
    className: 'border-warning/30 bg-warning-tint text-warning',
  },
  nao: { label: 'Não', icon: 'close', className: 'border-danger/30 bg-danger-tint text-danger' },
}

import type { Verdict } from './types'

export const VERDICT_VIEW: Record<Verdict, { label: string; icon: string; className: string }> = {
  sim: { label: 'Sim', icon: '✅', className: 'border-green-200 bg-green-50 text-green-900' },
  parcialmente: {
    label: 'Parcialmente',
    icon: '⚠️',
    className: 'border-amber-200 bg-amber-50 text-amber-900',
  },
  nao: { label: 'Não', icon: '❌', className: 'border-red-200 bg-red-50 text-red-900' },
}

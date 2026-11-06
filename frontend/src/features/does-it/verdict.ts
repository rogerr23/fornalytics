import type { TextCitation } from '../../shared/api/lens'
import type { Evidence, Verdict } from './types'

export const VERDICT_VIEW: Record<Verdict, { label: string; icon: string; className: string }> = {
  sim: { label: 'Sim', icon: '✅', className: 'border-green-200 bg-green-50 text-green-900' },
  parcialmente: {
    label: 'Parcialmente',
    icon: '⚠️',
    className: 'border-amber-200 bg-amber-50 text-amber-900',
  },
  nao: { label: 'Não', icon: '❌', className: 'border-red-200 bg-red-50 text-red-900' },
}

/** Evidence is already checked by the backend: it opens like a valid citation. */
export function evidenceToCitation(evidence: Evidence): TextCitation {
  return {
    marker: `[[${evidence.path}:L${evidence.line_start}-L${evidence.line_end}]]`,
    path: evidence.path,
    line_start: evidence.line_start,
    line_end: evidence.line_end,
    valid: true,
    problem: null,
  }
}

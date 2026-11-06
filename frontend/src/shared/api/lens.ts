/** Lens answers (overview and chat): shared event types and the lens vocabulary. */

import type { SseEvent } from './sse'

export type Lens = 'cliente' | 'nao_tecnico' | 'tecnico'

export const LENSES: { value: Lens; label: string; hint: string }[] = [
  { value: 'cliente', label: 'Cliente', hint: 'Valor e benefícios, sem jargão' },
  { value: 'nao_tecnico', label: 'Não técnico', hint: 'Como funciona na prática' },
  { value: 'tecnico', label: 'Técnico', hint: 'Arquitetura e código, com citações' },
]

export const LENS_LABEL: Record<Lens, string> = {
  cliente: 'Cliente',
  nao_tecnico: 'Não técnico',
  tecnico: 'Técnico',
}

export interface TextCitation {
  marker: string
  path: string
  line_start: number
  line_end: number
  valid: boolean
  problem: string | null
}

export type LensEvent =
  | { type: 'conversation'; conversation_id: string }
  | { type: 'delta'; text: string }
  | { type: 'citations'; citations: TextCitation[] }
  | { type: 'done'; cached: boolean; message_id: string | null }
  | { type: 'error'; message: string }

const LENS_EVENTS = new Set(['conversation', 'delta', 'citations', 'done', 'error'])

export function toLensEvent(event: SseEvent): LensEvent | null {
  if (!LENS_EVENTS.has(event.event)) return null
  return { type: event.event, ...JSON.parse(event.data) } as LensEvent
}

/** What the screen shows while an answer streams and after it ends. */
export interface AnswerState {
  text: string
  /** null until the `citations` event arrives (markers are shown as pending). */
  citations: TextCitation[] | null
  done: boolean
  cached: boolean
  error: string | null
}

export const EMPTY_ANSWER: AnswerState = {
  text: '',
  citations: null,
  done: false,
  cached: false,
  error: null,
}

export function reduceAnswer(state: AnswerState, event: LensEvent): AnswerState {
  switch (event.type) {
    case 'delta':
      return { ...state, text: state.text + event.text }
    case 'citations':
      return { ...state, citations: event.citations }
    case 'done':
      return { ...state, done: true, cached: event.cached }
    case 'error':
      return { ...state, done: true, error: event.message }
    default:
      return state
  }
}

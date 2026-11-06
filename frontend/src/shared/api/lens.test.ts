import { describe, expect, it } from 'vitest'
import { EMPTY_ANSWER, evidenceToCitation, reduceAnswer, toLensEvent, type LensEvent } from './lens'

describe('reduceAnswer', () => {
  it('builds the answer from the event sequence', () => {
    const events: LensEvent[] = [
      { type: 'conversation', conversation_id: 'c1' },
      { type: 'delta', text: 'Olá, ' },
      { type: 'delta', text: 'mundo.' },
      { type: 'citations', citations: [] },
      { type: 'done', cached: true, message_id: null },
    ]

    const answer = events.reduce(reduceAnswer, EMPTY_ANSWER)

    expect(answer).toEqual({
      text: 'Olá, mundo.',
      citations: [],
      done: true,
      cached: true,
      error: null,
    })
  })

  it('ends on an error event and keeps the partial text', () => {
    const answer = [
      { type: 'delta', text: 'Parte' } as const,
      { type: 'error', message: 'O limite gratuito da IA foi atingido.' } as const,
    ].reduce(reduceAnswer, EMPTY_ANSWER)

    expect(answer.text).toBe('Parte')
    expect(answer.done).toBe(true)
    expect(answer.citations).toBeNull()
    expect(answer.error).toContain('limite gratuito')
  })

  it('ignores unknown SSE events', () => {
    expect(toLensEvent({ event: 'status', data: '{}' })).toBeNull()
    expect(toLensEvent({ event: 'delta', data: '{"text":"a"}' })).toEqual({
      type: 'delta',
      text: 'a',
    })
  })
})

describe('evidenceToCitation', () => {
  it('turns checked evidence into an openable citation', () => {
    const citation = evidenceToCitation({
      source_type: 'code',
      path: 'src/coupon.py',
      line_start: 3,
      line_end: 9,
      quote: 'def apply_coupon',
    })

    expect(citation).toEqual({
      marker: '[[src/coupon.py:L3-L9]]',
      path: 'src/coupon.py',
      line_start: 3,
      line_end: 9,
      valid: true,
      problem: null,
    })
  })
})

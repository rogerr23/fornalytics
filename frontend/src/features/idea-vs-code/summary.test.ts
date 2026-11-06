import { describe, expect, it } from 'vitest'
import { STATE_MESSAGE, summaryText } from './summary'

describe('summaryText', () => {
  it('counts partial apart from delivered', () => {
    expect(summaryText({ promised: 5, implemented: 3, partial: 1 })).toBe(
      '3 de 5 promessas entregues (1 em parte)',
    )
    expect(summaryText({ promised: 1, implemented: 1, partial: 0 })).toBe(
      '1 de 1 promessa entregue',
    )
  })

  it('explains when there are no promises', () => {
    expect(summaryText({ promised: 0, implemented: 0, partial: 0 })).toMatch(/Nenhuma promessa/)
  })

  it('has a message for every state without comparison', () => {
    expect(Object.keys(STATE_MESSAGE).sort()).toEqual([
      'missing_code',
      'missing_idea',
      'no_promises',
    ])
  })
})

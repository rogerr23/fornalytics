import { describe, expect, it } from 'vitest'
import { evidenceToCitation, VERDICT_VIEW } from './verdict'

describe('does-it view', () => {
  it('has a label for every verdict', () => {
    expect(Object.keys(VERDICT_VIEW).sort()).toEqual(['nao', 'parcialmente', 'sim'])
  })

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

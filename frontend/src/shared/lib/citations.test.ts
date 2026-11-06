import { describe, expect, it } from 'vitest'
import { markersToLinks } from './citations'

describe('markersToLinks', () => {
  it('turns markers into citation links and reuses the index of repeated markers', () => {
    const { markdown, markers } = markersToLinks(
      'Ver [[src/cart_items.py:L10-L20]] e [[./README.md:L3]]. De novo [[src/cart_items.py:L10-L20]].',
    )

    expect(markers).toEqual(['[[src/cart_items.py:L10-L20]]', '[[./README.md:L3]]'])
    expect(markdown).toBe(
      'Ver [cart\\_items.py:10-20](cite:0) e [README.md:3](cite:1). De novo [cart\\_items.py:10-20](cite:0).',
    )
  })

  it('accepts spaces around the dash and leaves look-alikes alone', () => {
    const { markdown, markers } = markersToLinks('[[a.ts:L1 - L2]] [[sem linhas]] [b.ts:L1]')

    expect(markers).toEqual(['[[a.ts:L1 - L2]]'])
    expect(markdown).toBe('[a.ts:1-2](cite:0) [[sem linhas]] [b.ts:L1]')
  })
})

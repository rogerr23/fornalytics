import { describe, expect, it } from 'vitest'
import { VERDICT_VIEW } from './verdict'

describe('does-it view', () => {
  it('has a label for every verdict', () => {
    expect(Object.keys(VERDICT_VIEW).sort()).toEqual(['nao', 'parcialmente', 'sim'])
  })
})

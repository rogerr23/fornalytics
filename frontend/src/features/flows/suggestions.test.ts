import { describe, expect, it } from 'vitest'
import { flowSuggestions } from './suggestions'

describe('flowSuggestions', () => {
  it('turns base flow names into questions, without repeats', () => {
    expect(
      flowSuggestions(['Finalizar compra', ' Finalizar compra ', 'Login', 'Busca', 'Extra']),
    ).toEqual([
      'Como funciona: finalizar compra?',
      'Como funciona: login?',
      'Como funciona: busca?',
    ])
  })

  it('falls back to generic questions when the base has no flows', () => {
    expect(flowSuggestions([])).toHaveLength(2)
  })
})

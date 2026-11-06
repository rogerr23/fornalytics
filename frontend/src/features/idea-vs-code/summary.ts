import type { ComparisonState, IdeaVsCode } from './types'

/** "3 de 5 promessas entregues (1 em parte)". Partial is counted apart, never as delivered. */
export function summaryText(
  data: Pick<IdeaVsCode, 'promised' | 'implemented' | 'partial'>,
): string {
  const { promised, implemented, partial } = data
  if (promised === 0) return 'Nenhuma promessa encontrada no documento da ideia.'
  const total = `${implemented} de ${promised} ${promised === 1 ? 'promessa entregue' : 'promessas entregues'}`
  return partial > 0 ? `${total} (${partial} em parte)` : total
}

/** Why there is nothing to compare, when that is the case. */
export const STATE_MESSAGE: Record<Exclude<ComparisonState, 'available'>, string> = {
  missing_idea:
    'Só há código neste projeto. Envie o documento da ideia (escopo, transcrição ou texto) e reprocesse para comparar o prometido com o implementado.',
  missing_code:
    'Só há o documento da ideia. Tudo aparece como prometido e ainda não implementado; envie o código (.zip) e reprocesse para comparar.',
  no_promises:
    'O documento da ideia não trouxe funcionalidades prometidas. Confira se é o documento certo ou envie um escopo mais detalhado e reprocesse.',
}

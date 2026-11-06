const DEFAULT_SUGGESTIONS = [
  'O que acontece quando o usuário faz login?',
  'O que acontece quando um pedido é finalizado?',
]

/** Suggested questions from the base flow names, so the first click already works. */
export function flowSuggestions(names: string[], limit = 3): string[] {
  const unique = [...new Set(names.map((name) => name.trim()).filter(Boolean))]
  if (unique.length === 0) return DEFAULT_SUGGESTIONS
  return unique.slice(0, limit).map((name) => `Como funciona: ${name.toLowerCase()}?`)
}

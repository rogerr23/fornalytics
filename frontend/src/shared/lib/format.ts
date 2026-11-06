export function formatTokens(tokens: number): string {
  if (tokens >= 1000)
    return `${(tokens / 1000).toLocaleString('pt-BR', { maximumFractionDigits: 1 })} mil tokens`
  return `${tokens} tokens`
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
}

export function plural(count: number, singular: string, pluralForm = `${singular}s`): string {
  return `${count} ${count === 1 ? singular : pluralForm}`
}

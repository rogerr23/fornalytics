import type { Limits, SourceType } from '../../shared/api/projects'

export type SkipReason =
  | 'ignored_dir'
  | 'lockfile'
  | 'binary'
  | 'minified'
  | 'too_large'
  | 'secret'
  | 'unsafe_path'
  | 'empty'

export interface IngestionSummary {
  source_id: string
  source_type: SourceType
  filename: string | null
  files: { path: string; token_estimate: number }[]
  token_estimate: number
  skipped: { reason: SkipReason; count: number; examples: string[] }[]
  renamed: { original: string; stored_as: string }[]
  base_outdated: boolean
  limits: Limits
}

export type NewSource =
  | { kind: 'file'; type: SourceType; file: File }
  | { kind: 'text'; type: SourceType; title: string; content: string }
  | { kind: 'github'; url: string }

export const SKIP_LABEL: Record<SkipReason, string> = {
  ignored_dir: 'em pasta ignorada (node_modules, .git, build…)',
  lockfile: 'lockfile',
  binary: 'binário ou imagem',
  minified: 'minificado',
  too_large: 'acima de 200 KB',
  secret: 'possível segredo (.env, chave)',
  unsafe_path: 'caminho inseguro',
  empty: 'vazio',
}

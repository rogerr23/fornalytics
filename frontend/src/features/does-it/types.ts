import type { FeatureStatus } from '../../shared/lib/featureStatus'

export type Verdict = 'sim' | 'nao' | 'parcialmente'

export interface Evidence {
  source_type: string
  path: string
  line_start: number
  line_end: number
  quote: string
}

export interface DoesItResult {
  question: string
  verdict: Verdict
  feature: { name: string; status: FeatureStatus } | null
  justification: string
  evidence: Evidence[]
  adjusted: boolean
}

import type { Evidence } from '../../shared/api/lens'
import type { FeatureStatus } from '../../shared/lib/featureStatus'

export type Verdict = 'sim' | 'nao' | 'parcialmente'

export interface DoesItResult {
  question: string
  verdict: Verdict
  feature: { name: string; status: FeatureStatus } | null
  justification: string
  evidence: Evidence[]
  adjusted: boolean
}

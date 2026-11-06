import type { Evidence } from '../../shared/api/lens'
import type { FeatureStatus } from '../../shared/lib/featureStatus'

export type ComparisonState = 'available' | 'missing_idea' | 'missing_code' | 'no_promises'

export interface Feature {
  name: string
  description: string
  status: FeatureStatus
  promise_ref: string
  evidence: Evidence[]
}

export interface IdeaVsCode {
  state: ComparisonState
  columns: { delivered: Feature[]; missing: Feature[]; undocumented: Feature[] }
  promised: number
  implemented: number
  partial: number
  base_created_at: string
  base_outdated: boolean
}

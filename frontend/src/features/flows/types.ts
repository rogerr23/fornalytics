import type { Evidence } from '../../shared/api/lens'

export interface FlowStep {
  text: string
  evidence: Evidence[]
}

export interface Flow {
  name: string
  /** The question asked, or "" for a flow that comes from the product base. */
  question: string
  steps: FlowStep[]
  evidence: Evidence[]
  mermaid: string
  from_base: boolean
}

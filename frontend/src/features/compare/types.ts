import type { Lens, TextCitation } from '../../shared/api/lens'

export interface LensAnswer {
  lens: Lens
  text: string
  citations: TextCitation[]
}

export interface CompareResult {
  question: string
  answers: LensAnswer[]
}

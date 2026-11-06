import { createContext } from 'react'
import type { Lens } from '../../shared/api/lens'

export interface LensContextValue {
  lens: Lens
  setLens: (lens: Lens) => void
}

export const LensContext = createContext<LensContextValue | null>(null)

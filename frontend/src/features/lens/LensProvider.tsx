import { useState, type ReactNode } from 'react'
import { LENSES, type Lens } from '../../shared/api/lens'
import { readStored, writeStored } from '../../shared/lib/storage'
import { LensContext } from './context'

const STORAGE_KEY = 'fornalytics.lens'

function initialLens(): Lens {
  const stored = readStored(STORAGE_KEY)
  return LENSES.some((item) => item.value === stored) ? (stored as Lens) : 'nao_tecnico'
}

/** The active lens: one for the whole app, kept across tabs, projects and reloads. */
export function LensProvider({ children }: { children: ReactNode }) {
  const [lens, setLensState] = useState<Lens>(initialLens)

  function setLens(next: Lens) {
    setLensState(next)
    writeStored(STORAGE_KEY, next)
  }

  return <LensContext.Provider value={{ lens, setLens }}>{children}</LensContext.Provider>
}

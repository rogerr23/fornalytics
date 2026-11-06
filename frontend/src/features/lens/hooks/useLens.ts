import { useContext } from 'react'
import { LensContext, type LensContextValue } from '../context'

export function useLens(): LensContextValue {
  const value = useContext(LensContext)
  if (!value) throw new Error('useLens must be used inside <LensProvider>')
  return value
}

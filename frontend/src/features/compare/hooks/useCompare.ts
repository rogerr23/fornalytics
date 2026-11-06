import { useMutation } from '@tanstack/react-query'
import { compareLenses } from '../api'

/** One model call answers in the three lenses; results live only on this screen. */
export function useCompare(projectId: string) {
  return useMutation({ mutationFn: (question: string) => compareLenses(projectId, question) })
}

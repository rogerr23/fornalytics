import { useMutation, useQuery } from '@tanstack/react-query'
import type { Lens } from '../../../shared/api/lens'
import { askFlow, getBaseFlows } from '../api'

/** Flows already in the base (no AI call). */
export function useBaseFlows(projectId: string) {
  return useQuery({
    queryKey: ['projects', projectId, 'flows'],
    queryFn: ({ signal }) => getBaseFlows(projectId, signal),
  })
}

/** "O que acontece quando…?": one AI call. */
export function useAskFlow(projectId: string) {
  return useMutation({
    mutationFn: ({ question, lens }: { question: string; lens: Lens }) =>
      askFlow(projectId, question, lens),
  })
}

import { useMutation } from '@tanstack/react-query'
import type { Lens } from '../../../shared/api/lens'
import { askDoesIt } from '../api'

export function useDoesIt(projectId: string) {
  return useMutation({
    mutationFn: ({ question, lens }: { question: string; lens: Lens }) =>
      askDoesIt(projectId, question, lens),
  })
}

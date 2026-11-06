import { useMutation, useQueryClient } from '@tanstack/react-query'
import { projectKeys } from '../../../shared/api/projects'
import { addSource, deleteSource } from '../api'
import type { NewSource } from '../types'

function useInvalidateProject(projectId: string) {
  const queryClient = useQueryClient()
  return () =>
    Promise.all([
      queryClient.invalidateQueries({ queryKey: projectKeys.detail(projectId) }),
      queryClient.invalidateQueries({ queryKey: projectKeys.all, exact: true }),
    ])
}

export function useAddSource(projectId: string) {
  const invalidate = useInvalidateProject(projectId)
  return useMutation({
    mutationFn: (source: NewSource) => addSource(projectId, source),
    onSuccess: invalidate,
  })
}

export function useDeleteSource(projectId: string) {
  const invalidate = useInvalidateProject(projectId)
  return useMutation({
    mutationFn: (sourceId: string) => deleteSource(projectId, sourceId),
    onSuccess: invalidate,
  })
}

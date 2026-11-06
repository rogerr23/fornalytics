import {
  experimental_streamedQuery as streamedQuery,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'
import { projectKeys } from '../../../shared/api/projects'
import { startProcessing, streamStatus } from '../api'
import type { ProcessingProgress, ProcessingStatus } from '../types'

const statusKey = (projectId: string) => ['projects', projectId, 'status'] as const

function addStatus(progress: ProcessingProgress, status: ProcessingStatus): ProcessingProgress {
  const detail = status.status === 'processing' ? status.status_detail : null
  const steps =
    detail && progress.steps.at(-1) !== detail ? [...progress.steps, detail] : progress.steps
  return { current: status, steps }
}

/** Follows /status by SSE. Reloading the page reconnects and shows the current step. */
export function useProcessingStatus(projectId: string) {
  return useQuery({
    queryKey: statusKey(projectId),
    queryFn: streamedQuery({
      streamFn: ({ signal }) => streamStatus(projectId, signal),
      reducer: addStatus,
      initialValue: { current: null, steps: [] } as ProcessingProgress,
    }),
    staleTime: 0,
    gcTime: 0,
    retry: false,
  })
}

export function useStartProcessing(projectId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => startProcessing(projectId),
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: projectKeys.all }),
        queryClient.resetQueries({ queryKey: statusKey(projectId) }),
      ]),
  })
}

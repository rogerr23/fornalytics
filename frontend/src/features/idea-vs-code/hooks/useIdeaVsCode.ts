import { useQuery } from '@tanstack/react-query'
import { getIdeaVsCode } from '../api'

/** No model call: it only groups the base, so it is cheap to refetch. */
export function useIdeaVsCode(projectId: string) {
  return useQuery({
    queryKey: ['projects', projectId, 'idea-vs-code'],
    queryFn: ({ signal }) => getIdeaVsCode(projectId, signal),
  })
}

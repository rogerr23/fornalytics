import { experimental_streamedQuery as streamedQuery, useQuery } from '@tanstack/react-query'
import { EMPTY_ANSWER, reduceAnswer, type AnswerState, type Lens } from '../../../shared/api/lens'
import { streamOverview } from '../api'

/** Streams the overview on the first opening; switching back to a lens reuses the result. */
export function useOverview(projectId: string, lens: Lens) {
  return useQuery({
    queryKey: ['projects', projectId, 'overview', lens],
    queryFn: streamedQuery({
      streamFn: ({ signal }) => streamOverview(projectId, lens, signal),
      reducer: reduceAnswer,
      initialValue: EMPTY_ANSWER as AnswerState,
    }),
    staleTime: Infinity, // the server caches it until the project is reprocessed
    retry: false,
  })
}

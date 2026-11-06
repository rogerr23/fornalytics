import { useQuery, useQueryClient } from '@tanstack/react-query'

/**
 * Results kept for this browser session only (newest first), so switching tabs does not
 * lose them. Nothing is saved on the server.
 */
export function useSessionHistory<T>(key: readonly unknown[]) {
  const queryClient = useQueryClient()
  const history = useQuery<T[]>({
    queryKey: key,
    queryFn: () => [],
    initialData: [],
    staleTime: Infinity,
    gcTime: Infinity,
  })
  function add(item: T) {
    queryClient.setQueryData<T[]>(key, (items = []) => [item, ...items])
  }
  return [history.data, add] as const
}

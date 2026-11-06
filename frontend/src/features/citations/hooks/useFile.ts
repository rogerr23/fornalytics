import { useQuery } from '@tanstack/react-query'
import { getFile } from '../api'

export function useFile(projectId: string, path: string | null) {
  return useQuery({
    queryKey: ['projects', projectId, 'files', path],
    queryFn: ({ signal }) => getFile(projectId, path!, signal),
    enabled: path !== null,
    staleTime: Infinity, // a stored file only changes when its source is removed
  })
}

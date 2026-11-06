import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { projectKeys } from '../../../shared/api/projects'
import { createProject, listProjects } from '../api'

export function useProjects() {
  return useQuery({ queryKey: projectKeys.all, queryFn: ({ signal }) => listProjects(signal) })
}

export function useCreateProject() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createProject,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: projectKeys.all }),
  })
}

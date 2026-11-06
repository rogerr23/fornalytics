import { useState, type FormEvent } from 'react'
import { errorMessage } from '../../../shared/api/client'
import type { Project } from '../../../shared/api/projects'
import { Alert } from '../../../shared/ui/Alert'
import { Button } from '../../../shared/ui/Button'
import { useCreateProject } from '../hooks/useProjects'

export function CreateProjectForm({ onCreated }: { onCreated: (project: Project) => void }) {
  const [name, setName] = useState('')
  const create = useCreateProject()

  function submit(event: FormEvent) {
    event.preventDefault()
    if (name.trim()) create.mutate(name.trim(), { onSuccess: onCreated })
  }

  return (
    <form onSubmit={submit} className="flex flex-col gap-4">
      <label className="flex flex-col gap-1.5 text-sm font-medium text-gray-700">
        Nome do produto
        <input
          autoFocus
          value={name}
          onChange={(event) => setName(event.target.value)}
          maxLength={200}
          placeholder="Ex.: Loja online"
          className="rounded-lg border border-gray-300 px-3 py-2 text-base font-normal focus:border-indigo-500 focus:outline-none"
        />
      </label>
      {create.isError && <Alert tone="error">{errorMessage(create.error)}</Alert>}
      <div>
        <Button type="submit" disabled={!name.trim() || create.isPending}>
          {create.isPending ? 'Criando…' : 'Criar e enviar material'}
        </Button>
      </div>
    </form>
  )
}

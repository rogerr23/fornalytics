import { useState, type FormEvent } from 'react'
import { errorMessage } from '../../../shared/api/client'
import type { Project } from '../../../shared/api/projects'
import { Alert } from '../../../shared/ui/Alert'
import { Button } from '../../../shared/ui/Button'
import { FIELD, LABEL } from '../../../shared/ui/field'
import { Icon } from '../../../shared/ui/Icon'
import { useCreateProject } from '../hooks/useProjects'

export function CreateProjectForm({ onCreated }: { onCreated: (project: Project) => void }) {
  const [name, setName] = useState('')
  const create = useCreateProject()

  function submit(event: FormEvent) {
    event.preventDefault()
    if (name.trim()) create.mutate(name.trim(), { onSuccess: onCreated })
  }

  return (
    <form onSubmit={submit} className="flex flex-col gap-5">
      <label className={LABEL}>
        Nome do produto
        <input
          autoFocus
          value={name}
          onChange={(event) => setName(event.target.value)}
          maxLength={200}
          placeholder="Ex.: Loja online"
          className={`${FIELD} text-base font-normal`}
        />
        <span className="text-[13px] font-normal text-grey-500">
          Depois você envia o código e o documento da ideia.
        </span>
      </label>
      {create.isError && <Alert tone="error">{errorMessage(create.error)}</Alert>}
      <div>
        <Button type="submit" disabled={!name.trim() || create.isPending}>
          {create.isPending ? 'Criando…' : 'Criar e enviar material'}
          {!create.isPending && <Icon name="arrow" size={16} />}
        </Button>
      </div>
    </form>
  )
}

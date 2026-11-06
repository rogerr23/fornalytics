import { useState, type FormEvent } from 'react'
import { errorMessage } from '../../../shared/api/client'
import type { SourceType } from '../../../shared/api/projects'
import { Alert } from '../../../shared/ui/Alert'
import { Button } from '../../../shared/ui/Button'
import { Tabs } from '../../../shared/ui/Tabs'
import { useAddSource } from '../hooks/useSources'
import type { IngestionSummary, NewSource } from '../types'

type Mode = 'code' | 'document' | 'text'

const MODES = [
  { value: 'code' as const, label: 'Código (.zip)' },
  { value: 'document' as const, label: 'Documento' },
  { value: 'text' as const, label: 'Colar texto' },
]

const FIELD =
  'rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none'

interface SourceUploaderProps {
  projectId: string
  disabled?: boolean
  onUploaded: (summary: IngestionSummary) => void
}

export function SourceUploader({ projectId, disabled, onUploaded }: SourceUploaderProps) {
  const [mode, setMode] = useState<Mode>('code')
  const [file, setFile] = useState<File | null>(null)
  const [documentType, setDocumentType] = useState<SourceType>('idea_doc')
  const [textType, setTextType] = useState<SourceType>('text')
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [inputKey, setInputKey] = useState(0)
  const add = useAddSource(projectId)

  function reset() {
    setFile(null)
    setTitle('')
    setContent('')
    setInputKey((key) => key + 1) // clears the file input
  }

  function changeMode(next: Mode) {
    setMode(next)
    reset()
    add.reset()
  }

  function submit(event: FormEvent) {
    event.preventDefault()
    let source: NewSource | null = null
    if (mode === 'text' && content.trim()) source = { kind: 'text', type: textType, title, content }
    if (mode !== 'text' && file) {
      source = { kind: 'file', type: mode === 'code' ? 'code' : documentType, file }
    }
    if (!source) return
    add.mutate(source, {
      onSuccess: (summary) => {
        reset()
        onUploaded(summary)
      },
    })
  }

  const ready = mode === 'text' ? content.trim().length > 0 : file !== null

  return (
    <form onSubmit={submit} className="flex flex-col gap-4">
      <Tabs items={MODES} value={mode} onChange={changeMode} />

      {mode === 'code' && (
        <p className="text-sm text-gray-600">
          Um .zip do repositório. Pastas como node_modules e .git, binários, lockfiles e arquivos
          .env são ignorados automaticamente.
        </p>
      )}
      {mode === 'document' && (
        <label className="flex flex-col gap-1.5 text-sm font-medium text-gray-700">
          O que é este documento?
          <select
            value={documentType}
            onChange={(event) => setDocumentType(event.target.value as SourceType)}
            className={FIELD}
          >
            <option value="idea_doc">Documento da ideia / escopo</option>
            <option value="transcript">Transcrição de reunião</option>
          </select>
        </label>
      )}
      {mode !== 'text' && (
        <input
          key={inputKey}
          type="file"
          accept={mode === 'code' ? '.zip' : '.pdf,.docx,.md,.txt'}
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          className="text-sm file:mr-3 file:rounded-lg file:border-0 file:bg-indigo-50 file:px-3 file:py-2 file:font-medium file:text-indigo-700 hover:file:bg-indigo-100"
        />
      )}
      {mode === 'text' && (
        <div className="flex flex-col gap-3">
          <div className="flex flex-wrap gap-3">
            <input
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="Título (opcional)"
              className={`${FIELD} flex-1`}
            />
            <select
              value={textType}
              onChange={(event) => setTextType(event.target.value as SourceType)}
              className={FIELD}
            >
              <option value="text">Texto livre</option>
              <option value="transcript">Transcrição de reunião</option>
            </select>
          </div>
          <textarea
            value={content}
            onChange={(event) => setContent(event.target.value)}
            rows={6}
            placeholder="Cole aqui a descrição da ideia, o escopo ou a transcrição…"
            className={FIELD}
          />
        </div>
      )}

      {add.isError && <Alert tone="error">{errorMessage(add.error)}</Alert>}
      <div>
        <Button type="submit" disabled={disabled || !ready || add.isPending}>
          {add.isPending ? 'Lendo o material…' : 'Enviar'}
        </Button>
      </div>
    </form>
  )
}

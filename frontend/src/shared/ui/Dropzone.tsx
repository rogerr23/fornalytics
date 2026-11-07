import { useRef, useState, type DragEvent } from 'react'
import { Icon } from './Icon'

interface DropzoneProps {
  accept: string
  hint: string
  file: File | null
  disabled?: boolean
  onFile: (file: File | null) => void
}

/** Drag a file in or click to choose one. Uses the native file input (no library). */
export function Dropzone({ accept, hint, file, disabled, onFile }: DropzoneProps) {
  const input = useRef<HTMLInputElement>(null)
  const [over, setOver] = useState(false)

  function drop(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault()
    setOver(false)
    if (disabled) return
    onFile(event.dataTransfer.files[0] ?? null)
  }

  return (
    <div className="flex flex-col gap-2">
      <label
        onDragOver={(event) => {
          event.preventDefault()
          if (!disabled) setOver(true)
        }}
        onDragLeave={() => setOver(false)}
        onDrop={drop}
        className={`flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border border-dashed px-6 py-8 text-center transition-colors duration-150 ${
          over ? 'border-ink bg-grey-100' : 'border-grey-300 hover:border-ink hover:bg-grey-50'
        } ${disabled ? 'cursor-not-allowed opacity-60' : ''} has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-ink`}
      >
        <Icon name="upload" size={24} />
        <span className="text-sm font-semibold">
          Arraste o arquivo aqui ou{' '}
          <span className="underline underline-offset-4">escolha no computador</span>
        </span>
        <span className="text-xs text-grey-500">{hint}</span>
        <input
          ref={input}
          type="file"
          accept={accept}
          disabled={disabled}
          className="sr-only"
          onChange={(event) => onFile(event.target.files?.[0] ?? null)}
        />
      </label>
      {file && (
        <div className="flex items-center justify-between gap-3 rounded border border-grey-200 bg-grey-50 px-3.5 py-2.5 text-sm">
          <span className="flex min-w-0 items-center gap-2">
            <Icon name="file" size={16} className="shrink-0" />
            <span className="truncate font-medium">{file.name}</span>
          </span>
          <button
            type="button"
            onClick={() => {
              onFile(null)
              if (input.current) input.current.value = ''
            }}
            className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded hover:bg-grey-200"
            aria-label="Tirar o arquivo"
          >
            <Icon name="close" size={16} />
          </button>
        </div>
      )}
    </div>
  )
}

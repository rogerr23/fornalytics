import { useEffect, useRef } from 'react'
import { errorMessage } from '../../../shared/api/client'
import type { TextCitation } from '../../../shared/api/lens'
import { Alert } from '../../../shared/ui/Alert'
import { Button } from '../../../shared/ui/Button'
import { Icon } from '../../../shared/ui/Icon'
import { Spinner } from '../../../shared/ui/Spinner'
import { useFile } from '../hooks/useFile'

/** Side panel with the cited file, the cited lines highlighted and scrolled into view. */
export function CitationViewer({
  projectId,
  citation,
  onClose,
}: {
  projectId: string
  citation: TextCitation | null
  onClose: () => void
}) {
  const file = useFile(projectId, citation?.path ?? null)
  const firstLine = useRef<HTMLTableRowElement>(null)

  useEffect(() => {
    firstLine.current?.scrollIntoView({ block: 'center' })
  }, [file.data, citation])

  useEffect(() => {
    const close = (event: KeyboardEvent) => event.key === 'Escape' && onClose()
    window.addEventListener('keydown', close)
    return () => window.removeEventListener('keydown', close)
  }, [onClose])

  if (!citation) return null
  const lines = file.data?.content.split('\n') ?? []

  return (
    <div className="fixed inset-0 z-20 flex justify-end bg-black/60" onClick={onClose}>
      <aside
        role="dialog"
        aria-label={`Trecho de ${citation.path}`}
        aria-modal="true"
        className="flex h-full w-full max-w-3xl flex-col bg-white shadow-panel"
        onClick={(event) => event.stopPropagation()}
      >
        <header className="flex items-center justify-between gap-4 border-b border-grey-200 px-5 py-4">
          <div className="min-w-0">
            <p className="eyebrow text-grey-500">Trecho citado</p>
            <p className="truncate font-mono text-sm font-semibold">{citation.path}</p>
            <p className="text-xs text-grey-500">
              Linhas {citation.line_start}–{citation.line_end}
            </p>
          </div>
          <Button variant="secondary" size="sm" onClick={onClose} autoFocus>
            <Icon name="close" size={16} />
            Fechar
          </Button>
        </header>
        <div className="flex-1 overflow-auto">
          {file.isPending && (
            <div className="p-5">
              <Spinner label="Abrindo o arquivo…" />
            </div>
          )}
          {file.isError && (
            <div className="p-5">
              <Alert tone="error">{errorMessage(file.error)}</Alert>
            </div>
          )}
          {file.data && (
            <table className="w-full border-collapse font-mono text-[13px] leading-5">
              <tbody>
                {lines.map((line, index) => {
                  const number = index + 1
                  const cited = number >= citation.line_start && number <= citation.line_end
                  return (
                    <tr
                      key={number}
                      ref={number === citation.line_start ? firstLine : undefined}
                      className={cited ? 'bg-grey-200' : undefined}
                    >
                      <td
                        className={`w-14 border-r pr-3 text-right align-top select-none ${
                          cited
                            ? 'border-ink font-semibold text-ink'
                            : 'border-grey-200 text-grey-500'
                        }`}
                      >
                        {number}
                      </td>
                      <td className="pr-4 pl-3 break-all whitespace-pre-wrap text-ink-800">
                        {line || ' '}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          )}
        </div>
      </aside>
    </div>
  )
}

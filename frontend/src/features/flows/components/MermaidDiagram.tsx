import { useEffect, useId, useState } from 'react'
import { Spinner } from '../../../shared/ui/Spinner'

type MermaidApi = (typeof import('mermaid'))['default']

let loading: Promise<MermaidApi> | null = null

/** Mermaid is large: it is loaded only when the first diagram appears. */
function loadMermaid(): Promise<MermaidApi> {
  loading ??= import('mermaid').then(({ default: mermaid }) => {
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: 'strict',
      theme: 'base',
      themeVariables: {
        fontFamily: 'Montserrat Variable, sans-serif',
        primaryColor: '#ffffff',
        primaryBorderColor: '#000000',
        primaryTextColor: '#000000',
        lineColor: '#4a4a4a',
        edgeLabelBackground: '#f3f3f3',
      },
    })
    return mermaid
  })
  return loading
}

type State = { status: 'loading' } | { status: 'ready'; svg: string } | { status: 'failed' }

/** Draws the diagram. If drawing fails, the Mermaid text is shown instead (never a broken tab). */
export function MermaidDiagram({ text }: { text: string }) {
  const id = `mermaid-${useId().replace(/[^a-zA-Z0-9]/g, '')}`
  const [state, setState] = useState<State>({ status: 'loading' })

  useEffect(() => {
    let active = true
    loadMermaid()
      .then((mermaid) => mermaid.render(id, text))
      .then(({ svg }) => active && setState({ status: 'ready', svg }))
      .catch(() => {
        // On a parse error Mermaid leaves its error box at the end of <body>: remove it.
        document.getElementById(`d${id}`)?.remove()
        if (active) setState({ status: 'failed' })
      })
    return () => {
      active = false
    }
  }, [id, text])

  if (state.status === 'loading') return <Spinner label="Desenhando o diagrama…" />
  if (state.status === 'failed') {
    return (
      <div className="flex flex-col gap-1">
        <p className="text-xs text-grey-500">
          Não foi possível desenhar o diagrama. Texto do fluxo:
        </p>
        <pre className="overflow-x-auto rounded-lg border border-grey-200 bg-grey-50 p-3 text-xs text-ink-600">
          {text}
        </pre>
      </div>
    )
  }
  return (
    <div
      className="flex justify-center overflow-x-auto rounded-lg border border-grey-200 bg-grey-50 p-4 [&_svg]:max-w-full"
      // The SVG comes from Mermaid in strict mode, built from text escaped by the backend.
      dangerouslySetInnerHTML={{ __html: state.svg }}
    />
  )
}

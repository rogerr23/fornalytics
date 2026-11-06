import { useMemo, type ReactNode } from 'react'
import Markdown, { defaultUrlTransform, type Components } from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { TextCitation } from '../api/lens'
import { CITATION_SCHEME, markersToLinks } from '../lib/citations'

interface AnswerMarkdownProps {
  text: string
  /** null while streaming: markers show as pending until the `citations` event. */
  citations: TextCitation[] | null
  onOpenCitation: (citation: TextCitation) => void
}

/** A lens answer: Markdown where every [[path:Lx-Ly]] becomes a citation chip. */
export function AnswerMarkdown({ text, citations, onOpenCitation }: AnswerMarkdownProps) {
  const { markdown, markers } = useMemo(() => markersToLinks(text), [text])
  const byMarker = useMemo(
    () => new Map((citations ?? []).map((citation) => [citation.marker, citation])),
    [citations],
  )

  const components: Components = {
    ...MARKDOWN_COMPONENTS,
    a: ({ href, children }) => {
      if (!href?.startsWith(CITATION_SCHEME)) {
        return (
          <a href={href} target="_blank" rel="noreferrer" className="text-indigo-700 underline">
            {children}
          </a>
        )
      }
      const marker = markers[Number(href.slice(CITATION_SCHEME.length))]
      const citation = byMarker.get(marker)
      if (citations === null) {
        return (
          <CitationChip state="pending" title="Conferindo a citação…">
            {children}
          </CitationChip>
        )
      }
      if (!citation?.valid) {
        return (
          <CitationChip state="invalid" title="Citação não verificada: não confere com o material">
            {children} · não verificada
          </CitationChip>
        )
      }
      return (
        <CitationChip
          state="valid"
          title={`Abrir ${citation.path}`}
          onClick={() => onOpenCitation(citation)}
        >
          {children}
        </CitationChip>
      )
    },
  }

  return (
    <div className="flex flex-col gap-3 text-[15px] leading-relaxed text-gray-800">
      <Markdown remarkPlugins={[remarkGfm]} components={components} urlTransform={allowCitations}>
        {markdown}
      </Markdown>
    </div>
  )
}

function allowCitations(url: string): string {
  return url.startsWith(CITATION_SCHEME) ? url : defaultUrlTransform(url)
}

interface CitationChipProps {
  state: 'pending' | 'valid' | 'invalid'
  title: string
  onClick?: () => void
  children: ReactNode
}

const CHIP: Record<CitationChipProps['state'], string> = {
  pending: 'bg-gray-100 text-gray-500',
  valid: 'bg-indigo-50 text-indigo-700 hover:bg-indigo-100 cursor-pointer',
  invalid: 'bg-amber-50 text-amber-800 line-through decoration-amber-400',
}

function CitationChip({ state, title, onClick, children }: CitationChipProps) {
  const className = `mx-0.5 inline-flex items-center rounded px-1.5 py-0.5 align-baseline font-mono text-xs no-underline ${CHIP[state]}`
  if (onClick) {
    return (
      <button type="button" title={title} onClick={onClick} className={className}>
        {children}
      </button>
    )
  }
  return (
    <span title={title} className={className}>
      {children}
    </span>
  )
}

const MARKDOWN_COMPONENTS: Components = {
  h1: ({ children }) => <h2 className="mt-2 text-xl font-semibold text-gray-900">{children}</h2>,
  h2: ({ children }) => <h3 className="mt-2 text-lg font-semibold text-gray-900">{children}</h3>,
  h3: ({ children }) => <h4 className="mt-1 font-semibold text-gray-900">{children}</h4>,
  p: ({ children }) => <p>{children}</p>,
  ul: ({ children }) => <ul className="flex list-disc flex-col gap-1 pl-6">{children}</ul>,
  ol: ({ children }) => <ol className="flex list-decimal flex-col gap-1 pl-6">{children}</ol>,
  strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
  code: ({ children, className }) =>
    className ? (
      <code className={`${className} font-mono text-sm`}>{children}</code>
    ) : (
      <code className="rounded bg-gray-100 px-1 py-0.5 font-mono text-[13px] text-gray-800">
        {children}
      </code>
    ),
  pre: ({ children }) => (
    <pre className="overflow-x-auto rounded-lg bg-gray-900 p-3 text-gray-100">{children}</pre>
  ),
  table: ({ children }) => (
    <div className="overflow-x-auto">
      <table className="min-w-full border-collapse text-sm">{children}</table>
    </div>
  ),
  th: ({ children }) => (
    <th className="border border-gray-200 bg-gray-50 px-3 py-1.5 text-left font-semibold">
      {children}
    </th>
  ),
  td: ({ children }) => (
    <td className="border border-gray-200 px-3 py-1.5 align-top">{children}</td>
  ),
  blockquote: ({ children }) => (
    <blockquote className="border-l-4 border-gray-200 pl-4 text-gray-600">{children}</blockquote>
  ),
}

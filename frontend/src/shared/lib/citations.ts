/** Citation markers in answers: [[path:L10-L20]] or [[path:L10]] (same rule as the backend). */

const MARKER = /\[\[([^[\]\n]+?):L(\d+)(?:\s*-\s*L?(\d+))?\]\]/g

export const CITATION_SCHEME = 'cite:'

export interface MarkerLinks {
  /** The text with each marker turned into a Markdown link `[label](cite:N)`. */
  markdown: string
  /** Marker texts, indexed by N. */
  markers: string[]
}

export function markersToLinks(text: string): MarkerLinks {
  const markers: string[] = []
  const markdown = text.replace(MARKER, (marker, path: string, start: string, end?: string) => {
    let index = markers.indexOf(marker)
    if (index === -1) index = markers.push(marker) - 1
    return `[${escapeLabel(citationLabel(path, Number(start), Number(end ?? start)))}](${CITATION_SCHEME}${index})`
  })
  return { markdown, markers }
}

export function citationLabel(path: string, start: number, end: number): string {
  const name = path.trim().split('/').pop() || path
  return start === end ? `${name}:${start}` : `${name}:${start}-${end}`
}

function escapeLabel(label: string): string {
  return label.replace(/([\\`*_[\]])/g, '\\$1')
}

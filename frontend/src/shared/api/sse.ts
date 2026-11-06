/** Server-Sent Events over fetch (no extra library). Contract in docs/api-events.md. */

export interface SseEvent {
  event: string
  data: string
}

/** Turns text chunks into complete events; a chunk may end in the middle of an event. */
export class SseParser {
  private buffer = ''

  push(chunk: string): SseEvent[] {
    this.buffer += chunk.replace(/\r\n?/g, '\n')
    const events: SseEvent[] = []
    let end = this.buffer.indexOf('\n\n')
    while (end !== -1) {
      const block = this.buffer.slice(0, end)
      this.buffer = this.buffer.slice(end + 2)
      const event = parseBlock(block)
      if (event) events.push(event)
      end = this.buffer.indexOf('\n\n')
    }
    return events
  }
}

function parseBlock(block: string): SseEvent | null {
  let event = 'message'
  const data: string[] = []
  for (const line of block.split('\n')) {
    if (!line || line.startsWith(':')) continue // comments (": ping") keep the stream alive
    const colon = line.indexOf(':')
    const field = colon === -1 ? line : line.slice(0, colon)
    const value = colon === -1 ? '' : line.slice(colon + 1).replace(/^ /, '')
    if (field === 'event') event = value
    else if (field === 'data') data.push(value)
  }
  return data.length ? { event, data: data.join('\n') } : null
}

export async function* readSse(response: Response): AsyncGenerator<SseEvent> {
  if (!response.body) return
  const reader = response.body.pipeThrough(new TextDecoderStream()).getReader()
  const parser = new SseParser()
  try {
    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      yield* parser.push(value)
    }
  } finally {
    reader.releaseLock()
  }
}

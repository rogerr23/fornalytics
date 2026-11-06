import { describe, expect, it } from 'vitest'
import { SseParser } from './sse'

describe('SseParser', () => {
  it('joins an event split across chunks', () => {
    const parser = new SseParser()

    expect(parser.push('event: delta\ndata: {"te')).toEqual([])
    expect(parser.push('xt":"oi"}\n\nevent: done\n')).toEqual([
      { event: 'delta', data: '{"text":"oi"}' },
    ])
    expect(parser.push('data: {}\n\n')).toEqual([{ event: 'done', data: '{}' }])
  })

  it('ignores comments (heartbeats) and handles CRLF and multi-line data', () => {
    const parser = new SseParser()

    const events = parser.push(': ping\r\n\r\nevent: status\r\ndata: a\r\ndata: b\r\n\r\n')

    expect(events).toEqual([{ event: 'status', data: 'a\nb' }])
  })

  it('defaults the event name to message', () => {
    expect(new SseParser().push('data: x\n\n')).toEqual([{ event: 'message', data: 'x' }])
  })
})

import { apiFetch } from './client'
import { toLensEvent, type LensEvent } from './lens'
import { readSse } from './sse'

/** Opens a lens answer stream (overview or chat) and yields its events. */
export async function* streamLensEvents(
  path: string,
  init: RequestInit,
): AsyncGenerator<LensEvent> {
  const response = await apiFetch(path, init)
  for await (const event of readSse(response)) {
    const lensEvent = toLensEvent(event)
    if (lensEvent) yield lensEvent
  }
}

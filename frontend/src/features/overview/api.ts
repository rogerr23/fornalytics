import type { Lens, LensEvent } from '../../shared/api/lens'
import { streamLensEvents } from '../../shared/api/lensStream'

export function streamOverview(
  projectId: string,
  lens: Lens,
  signal: AbortSignal,
): AsyncGenerator<LensEvent> {
  return streamLensEvents(`/projects/${projectId}/overview?lens=${lens}`, { signal })
}

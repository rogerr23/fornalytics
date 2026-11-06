import { apiGet } from '../../shared/api/client'
import type { Lens, LensEvent } from '../../shared/api/lens'
import { streamLensEvents } from '../../shared/api/lensStream'
import type { Conversation } from './types'

export function streamChat(
  projectId: string,
  body: { lens: Lens; question: string; conversation_id: string | null },
  signal?: AbortSignal,
): AsyncGenerator<LensEvent> {
  return streamLensEvents(`/projects/${projectId}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    signal,
  })
}

export function getConversation(
  projectId: string,
  conversationId: string,
  signal?: AbortSignal,
): Promise<Conversation> {
  return apiGet<Conversation>(`/projects/${projectId}/conversations/${conversationId}`, signal)
}
